from parsimonious import Grammar
from parsimonious.nodes import Node

from libddog.metrics.bases import QueryNode
from libddog.parsing.query_visitor import QueryVisitor


class QueryParser:
    def __init__(self) -> None:
        content = open("libddog/parsing/grammar.txt").read()
        self.grammar = Grammar(content)

    def parse(self, query_string: str) -> Node:
        return self.grammar.parse(query_string)

    def parse_ast(self, query_string: str) -> QueryNode:
        st = self.parse(query_string)
        visitor = QueryVisitor()
        ast: QueryNode = visitor.visit(st)
        # import pdb; pdb.set_trace()
        return ast
