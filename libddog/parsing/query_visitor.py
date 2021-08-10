import enum
from typing import Any, List

from parsimonious.exceptions import VisitationError
from parsimonious.nodes import NodeVisitor, Node

from libddog.metrics.query import AggFunc, Aggregation, Metric, Query


class ParseError(Exception):
    pass


def reverse_enum(enum_cls: enum.Enum, literal: str) -> enum.Enum:
    for alternative in list(enum_cls):
        if literal == alternative.value:
            return alternative

    raise ParseError("Failed to reverse enum %r using input: %r" % (enum_cls, literal))


class QueryVisitor(NodeVisitor):
    # query

    def visit_query(self, node: Node, visited_children: List[Node]) -> Any:
        agg_func = visited_children[0]
        name = visited_children[1]
        return Query(metric=Metric(name=name), agg=Aggregation(func=agg_func))

    def visit_agg(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children[0]

    def visit_agg_func(self, node: Node, visited_children: List[Node]) -> Any:
        return reverse_enum(AggFunc, node.text)

    def visit_metric_name(self, node: Node, visited_children: List[Node]) -> Any:
        elems = [visited_children[0].text]

        for dot, part in visited_children[1]:
            elems.extend([dot.text, part[0].text])

        return "".join(elems)

    # catch all

    def generic_visit(self, node: Node, visited_children: List[Node]) -> Any:
        return visited_children or node
