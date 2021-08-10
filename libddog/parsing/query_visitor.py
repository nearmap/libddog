import enum
from typing import Any, List, Type

from parsimonious.nodes import Node, NodeVisitor

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
    Query,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
)


class ParseError(Exception):
    pass


def reverse_enum(enum_cls: Type[enum.Enum], literal: str) -> enum.Enum:
    alternatives: List[enum.Enum] = list(enum_cls)
    for alternative in alternatives:
        if literal == alternative.value:
            return alternative

    raise ParseError("Failed to reverse enum %r using input: %r" % (enum_cls, literal))


class QueryVisitor(NodeVisitor):  # type: ignore
    def visit_program(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    # expr

    def visit_expr(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_formula(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_expr_ex_formula(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_operand(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

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

        # import pdb; pdb.set_trace()
        return Query(
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

        minus = visited_children[5][0][3][0].text
        period = visited_children[5][0][3][1].text

        if period:
            period = int(period)
            if minus == "-":
                period = -period

        return Rollup(func=func, period_s=period)

    def visit_rollup_func(self, node: Node, visited_children: List[Node]) -> Any:
        return reverse_enum(RollupFunc, node.text)

    def visit_fill(self, node: Node, visited_children: List[Node]) -> Any:
        func = visited_children[4]

        minus = visited_children[5][0][3][0].text
        limit = visited_children[5][0][3][1].text

        if limit:
            limit = int(limit)
            if minus == "-":
                limit = -limit

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

    # catch all

    def generic_visit(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children or node
