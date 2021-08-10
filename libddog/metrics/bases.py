class QueryNode:
    "The base class for all metrics AST classes."

    def codegen(self) -> str:
        raise NotImplemented
