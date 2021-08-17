import enum
from typing import Any, List, Type

from parsimonious.nodes import Node, NodeVisitor

import libddog.metrics.formulas
import libddog.metrics.functions
from libddog.metrics.formulas import BinaryFormula, Comma
from libddog.metrics.functions import Function
from libddog.metrics.literals import Int
from libddog.metrics.query import (
    AggFunc,
    Aggregation,
    As,
    By,
    Fill,
    FillFunc,
    Filter,
    FilterOperator,
    Metric,
    QueryState,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
)


class ParseError(Exception):
    pass


def resolve_binop(symbol: str) -> Type[BinaryFormula]:
    mod = libddog.metrics.formulas
    for attname in dir(mod):
        cls = getattr(mod, attname)
        if issubclass(cls, BinaryFormula) and cls.symbol == symbol:
            return cls  # type: ignore

    raise ParseError("Failed to resolve binary operator using input: %r" % symbol)


def reverse_enum(enum_cls: Type[enum.Enum], literal: str) -> enum.Enum:
    alternatives: List[enum.Enum] = list(enum_cls)
    for alternative in alternatives:
        if literal == alternative.value:
            return alternative

    raise ParseError("Failed to reverse enum %r using input: %r" % (enum_cls, literal))


def resolve_func(func_name: str) -> Type[Function]:
    mod = libddog.metrics.functions
    for attname in dir(mod):
        cls = getattr(mod, attname)
        try:
            if issubclass(cls, Function) and func_name == attname:
                return cls  # type: ignore
        except TypeError:
            pass  # issubclass raised

    raise ParseError("Failed to resolve function name using input: %r" % func_name)


class QueryVisitor(NodeVisitor):  # type: ignore
    def visit_program(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    # expr

    def visit_expr(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_formula(self, node: Node, visited_children: List[Node]) -> Any:
        left = visited_children[0]
        binop = left

        operator, right = None, None
        if isinstance(visited_children[1], list):
            operator = visited_children[1][0][1]
            right = visited_children[1][0][3]

        if operator and right:
            binop_cls = resolve_binop(operator)
            if isinstance(right, int):
                right = Int(right)
            # elif isinstance(right, str):
            #     right = Str(right)
            binop = binop_cls(left, right)

        return binop

    def visit_expr_ex_formula(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_func_call(self, node: Node, visited_children: List[Node]) -> Any:
        name = visited_children[0]

        fst = visited_children[3]
        args = [fst]

        # we run into a problem here because the arguments to the function have
        # already been parsed as a Comma binop and we have to actually undo that
        # here
        if isinstance(fst, Comma):
            left: Any = fst.left
            right: Any = fst.right

            assert not isinstance(left, Comma)
            assert not isinstance(right, Comma)

            if isinstance(left, Int):
                left = left.value
            if isinstance(right, Int):
                right = right.value

            args = [left, right]

        func = resolve_func(name)
        return func(*args)

    def visit_paren_expr(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[2]

    def visit_operand(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_binop(self, node: Node, visited_children: List[Node]) -> Any:
        return node.text

    def visit_func_name(self, node: Node, visited_children: List[Node]) -> Any:
        return node.text

    # query

    def visit_query(self, node: Node, visited_children: List[Node]) -> Any:
        agg_func = None
        if visited_children[0]:
            agg_func = visited_children[0][0]

        name = visited_children[1]

        filter = None
        if isinstance(visited_children[2], list):
            filter = visited_children[2][0]

        by = None
        if isinstance(visited_children[3], list):
            by = visited_children[3][0]

        as_ = None
        if isinstance(visited_children[4], list):
            as_ = visited_children[4][0]

        funcs = []
        if isinstance(visited_children[5], list):
            for rest in visited_children[5]:
                funcs.append(rest[0])

        agg = None
        if agg_func:
            agg = Aggregation(func=agg_func, by=by, as_=as_)

        return QueryState(
            metric=Metric(name=name),
            agg=agg,
            filter=filter,
            funcs=funcs,
        )

    def visit_agg(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_agg_func(self, node: Node, visited_children: List[Node]) -> Any:
        return reverse_enum(AggFunc, node.text)

    def visit_metric_name(self, node: Node, visited_children: List[Node]) -> Any:
        elems = [visited_children[0].text]

        for dot, part in visited_children[1]:
            elems.extend([dot.text, part[0].text])

        return "".join(elems)

    def visit_filter(self, node: Node, visited_children: List[Node]) -> Any:
        cond = visited_children[2]
        conds = [cond]

        for rest in visited_children[3]:
            cond = rest[3]
            conds.append(cond)

        return Filter(conds=conds)

    def visit_filter_item(self, node: Node, visited_children: List[Node]) -> Any:
        if isinstance(visited_children[0], Tag):
            return visited_children[0]

        elif visited_children[0].startswith("$") and len(visited_children[0]) > 1:
            return TmplVar(tvar=visited_children[0][1:])

        raise ParseError("Unsupported filter item: %r" % node)

    def visit_filter_keyval(self, node: Node, visited_children: List[Node]) -> Any:
        bang = node.children[0].text
        tag = node.children[1].text
        colon_value = node.children[2].text

        op = FilterOperator.NOT_EQUAL if bang == "!" else FilterOperator.EQUAL
        value = colon_value[1:] if colon_value else None

        return Tag(tag=tag, value=value, operator=op)

    def visit_by(self, node: Node, visited_children: List[Node]) -> Any:
        item = visited_children[5]
        tags = [item]

        for rest in visited_children[6]:
            item = rest[3]
            tags.append(item)

        return By(tags=tags)

    def visit_by_item(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_as(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[2]

    def visit_as_func(self, node: Node, visited_children: List[Node]) -> Any:
        return reverse_enum(As, node.text)

    def visit_query_func(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children

    def visit_rollup(self, node: Node, visited_children: List[Node]) -> Any:
        func = visited_children[4]
        period = visited_children[5][0][3]
        return Rollup(func=func, period_s=period)

    def visit_rollup_func(self, node: Node, visited_children: List[Node]) -> Any:
        return reverse_enum(RollupFunc, node.text)

    def visit_fill(self, node: Node, visited_children: List[Node]) -> Any:
        func = visited_children[4]
        limit = visited_children[5][0][3]
        return Fill(func=func, limit_s=limit)

    def visit_fill_arg(self, node: Node, visited_children: List[Node]) -> Any:
        try:
            arg = reverse_enum(FillFunc, node.text)
        except ParseError:
            # if it's an integer it must be 0
            assert int(node.text) == 0
            arg = FillFunc.ZERO

        return arg

    # atoms

    def visit_tag_name(self, node: Node, visited_children: List[Node]) -> Any:
        return node.text

    def visit_tvar_name(self, node: Node, visited_children: List[Node]) -> Any:
        dollar = node.children[0].text
        tvar = node.children[1].text
        return f"{dollar}{tvar}"

    def visit_integer(self, node: Node, visited_children: List[Node]) -> Any:
        if isinstance(visited_children[0], list):
            minus = visited_children[0][0].text
        else:
            minus = visited_children[0].text

        num = visited_children[1].text

        num = int(num)
        if minus == "-":
            num = -num

        return num

    # catch all

    def generic_visit(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children or node
