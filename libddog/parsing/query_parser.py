from pathlib import Path

from parsimonious import Grammar
from parsimonious.exceptions import IncompleteParseError, ParseError
from parsimonious.nodes import Node

from libddog.metrics.bases import QueryNode


class QueryParser:
    _instance = None

    def __init__(self) -> None:
        proj_root = Path(__file__).parent
        grammar_filepath = proj_root.joinpath("grammar.txt").absolute()
        content = open(grammar_filepath).read()
        self.grammar = Grammar(content)

    @classmethod
    def get_instance(cls) -> "QueryParser":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def parse_st(self, query_string: str) -> Node:
        return self.grammar.parse(query_string)

    def parse_ast(self, query_string: str) -> QueryNode:
        from libddog.parsing.query_visitor import QueryVisitor

        st = self.parse_st(query_string)
        visitor = QueryVisitor()
        ast: QueryNode = visitor.visit(st)
        return ast

    def is_valid_tag_name(self, token: str) -> bool:
        try:
            self.grammar["tag_name"].parse(token)
        except (IncompleteParseError, ParseError) as exc:
            return False

        return True

    def is_valid_tmpl_var(self, token: str) -> bool:
        try:
            self.grammar["tvar_name"].parse(token)
        except (IncompleteParseError, ParseError) as exc:
            return False

        return True

    def is_valid_tag_value(self, token: str) -> bool:
        try:
            self.grammar["tag_value"].parse(token)
        except (IncompleteParseError, ParseError) as exc:
            return False

        return True
