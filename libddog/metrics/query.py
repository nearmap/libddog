import copy
import enum
from typing import Any, Dict, List, Optional, Type

from libddog.common.bases import Renderable
from libddog.metrics.bases import QueryNode
from libddog.metrics.literals import Identifier


class QueryValidationError(Exception):
    pass


def reverse_enum(enum_cls: Type[enum.Enum], literal: str, label: str) -> enum.Enum:
    alternatives: List[enum.Enum] = list(enum_cls)
    for alternative in alternatives:
        if literal == alternative.value:
            return alternative

    values = [alt.value for alt in alternatives]
    values_fmt = ", ".join([f"{alt!r}" for alt in sorted(values)])
    raise QueryValidationError("%s %r must be one of %s" % (label, literal, values_fmt))


class Metric(QueryNode):
    def __init__(self, *, name: str) -> None:
        self.name = name

    def codegen(self) -> str:
        return self.name


class FilterOperator(enum.Enum):
    EQUAL = 1
    NOT_EQUAL = 2


class FilterCond(QueryNode):
    pass


class Tag(FilterCond):
    def __init__(
        self,
        *,
        tag: str,
        value: Optional[str] = None,
        operator: FilterOperator = FilterOperator.EQUAL,
    ) -> None:
        self.tag = tag
        self.value = value
        self.operator = operator

    def codegen(self) -> str:
        key = self.tag
        colon_value = ""

        if self.operator is FilterOperator.NOT_EQUAL:
            key = f"!{key}"

        if self.value is not None:
            colon_value = f":{self.value}"

        return f"{key}{colon_value}"


class TmplVar(FilterCond):
    """A filter using a template variable."""

    def __init__(self, *, tvar: str) -> None:
        assert not tvar.startswith("$")

        self.tvar = tvar

    def codegen(self) -> str:
        return "$%s" % self.tvar


class Filter(QueryNode):
    def __init__(self, *, conds: List[FilterCond]) -> None:
        self.conds = conds

    def codegen(self) -> str:
        return "{%s}" % ", ".join((cond.codegen() for cond in self.conds))

    def __and__(self, other: Optional["Filter"]) -> "Filter":
        if other:
            conds = self.conds + other.conds
            return self.__class__(conds=conds)

        return self


class AggFunc(enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"

    def codegen(self) -> str:
        return self.value


class By(QueryNode):
    def __init__(self, *, tags: List[str]) -> None:
        self.tags = tags

    def codegen(self) -> str:
        return " by {%s}" % ", ".join((tag for tag in self.tags))


class As(enum.Enum):
    RATE = "rate"
    COUNT = "count"

    def codegen(self) -> str:
        return ".as_%s()" % self.value


class Aggregation(QueryNode):
    def __init__(
        self, *, func: AggFunc, by: Optional[By] = None, as_: Optional[As] = None
    ) -> None:
        self.func = func
        self.by = by
        self.as_ = as_  # 'as' is a keyword in Python


class QueryFunc(QueryNode):
    """
    A QueryFunc is attached directly to a Query. This makes it different from
    other functions modeled as derived from Function because they can be applied
    to whole expressions.
    """


class RollupFunc(enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"
    DEFAULT = ""  # yes, it's supposed to be the empty string

    def codegen(self) -> str:
        return self.value


class Rollup(QueryFunc):
    def __init__(self, *, func: RollupFunc, period_s: Optional[int] = None) -> None:
        self.func = func
        self.period_s = period_s

    def codegen(self) -> str:
        period_s = "%s" % self.period_s if self.period_s else ""
        args = [
            self.func.codegen(),
            period_s,
        ]
        args = [arg for arg in args if arg]

        # func == DEFAULT and period_s unset
        if not args:
            return ""

        return ".rollup(%s)" % ", ".join(args)


class FillFunc(enum.Enum):
    LINEAR = "linear"
    LAST = "last"
    ZERO = "zero"
    NULL = "null"


class Fill(QueryFunc):
    def __init__(self, *, func: FillFunc, limit_s: int = 300) -> None:
        self.func = func
        self.limit_s = limit_s

    def codegen(self) -> str:
        limit_s = "%s" % self.limit_s if self.limit_s else ""
        args = [self.func.value, limit_s]
        args = [arg for arg in args if arg]
        return ".fill(%s)" % ", ".join(args)


class QueryState(QueryNode, Renderable):
    _instance_counter = 1

    def __init__(
        self,
        *,
        metric: Metric,
        filter: Optional[Filter] = None,
        agg: Optional[Aggregation] = None,
        funcs: Optional[List[QueryFunc]] = None,
        name: Optional[str] = None,
        data_source: str = "metrics",
        aggregator: str = "unused",  # TODO: remove
        query: str = "unused",  # TODO: remove
    ) -> None:
        self.metric = metric
        self.filter = filter
        self.agg = agg
        self.funcs = funcs or []
        self.name = name or self.get_next_unique_name()
        self.data_source = data_source
        self.aggregator = aggregator
        self.query = query

    def clone(self) -> "QueryState":
        return copy.deepcopy(self)

    def get_next_unique_name(self) -> str:
        counter = self.__class__._instance_counter
        self.__class__._instance_counter += 1
        return "q%s" % counter

    def identifier(self) -> Identifier:
        return Identifier(self.name)

    def codegen(self) -> str:
        agg_func, agg_by, agg_as = "", "", ""
        if self.agg:
            agg_func = "%s:" % self.agg.func.codegen()
            agg_by = self.agg.by.codegen() if self.agg.by else ""
            agg_as = self.agg.as_.codegen() if self.agg.as_ else ""

        metric = self.metric.codegen()
        filter = self.filter.codegen() if self.filter else "{*}"

        funcs = "".join([func.codegen() for func in self.funcs])

        query = "%s%s%s%s%s%s" % (
            agg_func,
            metric,
            filter,
            agg_by,
            agg_as,
            funcs,
        )

        return query

    def as_dict(self) -> Dict[str, Any]:
        dct = {
            # self.agg would only be unset for legacy query strings, and 'avg'
            # is the default aggregation anyway
            "aggregator": self.agg.func.value if self.agg else "avg",
            "data_source": self.data_source,
            "name": self.name,
            "query": self.codegen(),
        }

        return dct


class QueryMonad:
    def __init__(self, state: QueryState) -> None:
        self._state = state

    def agg(self, func: str) -> "QueryMonad":
        state = self._state.clone()

        agg_func_existing = state.agg.func if state.agg else None
        if agg_func_existing is not None:
            raise QueryValidationError(
                "Cannot set aggregation function %r because "
                "query already contains aggregation function %r"
                % (func, agg_func_existing.value)
            )

        agg_func = reverse_enum(AggFunc, func, label="Aggregation function")
        assert isinstance(agg_func, AggFunc)  # help mypy
        state.agg = Aggregation(func=agg_func)

        return self.__class__(state)

    def by(self, *tags: str) -> 'QueryMonad':
        state = self._state.clone()

        # TODO: validate that tags are well formed

        # 'func' has to be set before 'by' - otherwise it would be possible to
        # construct queries with 'by' only and that wouldn't be valid syntax
        if not state.agg:
            tags_fmt = ', '.join([f"{tag!r}" for tag in tags])
            raise QueryValidationError(
                "Cannot set aggregation by %s because "
                "aggregation function is not set yet"
                % tags_fmt
            )

        by = state.agg.by or By(tags=list(tags))
        for tag in tags:
            if tag not in by.tags:
                by.tags.append(tag)

        state.agg.by = by
        return self.__class__(state)


def Query(metric: str, name: Optional[str] = None) -> QueryMonad:
    state = QueryState(metric=Metric(name=metric), name=name)
    return QueryMonad(state)
