import enum
from typing import Any, Dict, List, Optional

from libddog.common.bases import Renderable


class ASTNode:
    def codegen(self) -> str:
        raise NotImplemented


class Metric(ASTNode):
    def __init__(self, *, name: str) -> None:
        self.name = name

    def codegen(self) -> str:
        return self.name


class FilterCond(ASTNode):
    pass


class Tag(FilterCond):
    def __init__(self, *, tag: str, value: str) -> None:
        self.tag = tag
        self.value = value

    def codegen(self) -> str:
        return "%s:%s" % (self.tag, self.value)


class TmplVar(FilterCond):
    """A filter using a template variable."""

    def __init__(self, *, tvar: str) -> None:
        assert not tvar.startswith("$")

        self.tvar = tvar

    def codegen(self) -> str:
        return "$%s" % self.tvar


class Filter(ASTNode):
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


class By(ASTNode):
    def __init__(self, *, tags: List[str]) -> None:
        self.tags = tags

    def codegen(self) -> str:
        return " by {%s}" % ", ".join((tag for tag in self.tags))


class As(enum.Enum):
    RATE = "rate"
    COUNT = "count"

    def codegen(self) -> str:
        return ".as_%s()" % self.value


class Aggregation(ASTNode):
    def __init__(
        self, *, func: AggFunc, by: Optional[By] = None, as_: Optional[As] = None
    ) -> None:
        self.func = func
        self.by = by
        self.as_ = as_


class RollupFunc(enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"
    DEFAULT = ""  # yes, it's supposed to be the empty string

    def codegen(self) -> str:
        return self.value


class Rollup(ASTNode):
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
        return ".rollup(%s)" % ", ".join(args)


class Query(ASTNode, Renderable):
    _instance_counter = 1

    def __init__(
        self,
        *,
        metric: Metric,
        filter: Optional[Filter] = None,
        agg: Aggregation,
        rollup: Optional[Rollup] = None,
        name: Optional[str] = None,
        data_source: str = "metrics",
        aggregator: str = "unused",  # ignore me
        query: str = "unused",  # ignore me
    ) -> None:
        self.metric = metric
        self.filter = filter
        self.agg = agg
        self.rollup = rollup
        self.name = name or self.get_next_unique_name()
        self.data_source = data_source
        self.aggregator = aggregator
        self.query = query

    def get_next_unique_name(self) -> str:
        counter = self._instance_counter
        self._instance_counter += 1
        return "q%s" % counter

    def codegen(self) -> str:
        agg_func = self.agg.func.codegen()
        agg_by = self.agg.by.codegen() if self.agg.by else ""
        agg_as = self.agg.as_.codegen() if self.agg.as_ else ""
        metric = self.metric.codegen()
        filter = self.filter.codegen() if self.filter else ""
        rollup = self.rollup.codegen() if self.rollup else ""

        query = "%s:%s%s%s%s%s" % (
            agg_func,
            metric,
            filter,
            agg_by,
            agg_as,
            rollup,
        )

        return query

    def as_dict(self) -> Dict[str, Any]:
        dct = {
            "aggregator": self.agg.func.value,
            "data_source": self.data_source,
            "query": self.codegen(),
        }

        if self.name:
            dct["name"] = self.name

        return dct
