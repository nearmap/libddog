from parsimonious import Grammar
from parsimonious.nodes import Node


class QueryParser:
    def __init__(self) -> None:
        content = open("libddog/parsing/grammar.txt").read()
        self.grammar = Grammar(content)

    def parse(self, query_string: str) -> Node:
        return self.grammar.parse(query_string)
