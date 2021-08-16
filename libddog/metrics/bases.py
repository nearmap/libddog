class QueryNode:
    "The base class for all metrics AST classes."

    def codegen(self) -> str:
        raise NotImplemented


class FormulaNode:
    "The base class for all formula AST classes."

    def codegen(self) -> str:
        raise NotImplemented

    def __add__(self, other: "FormulaNode") -> "FormulaNode":
        from libddog.metrics.formulas import Add

        return Add(self, other)

    def __sub__(self, other: "FormulaNode") -> "FormulaNode":
        from libddog.metrics.formulas import Sub

        return Sub(self, other)

    def __mul__(self, other: "FormulaNode") -> "FormulaNode":
        from libddog.metrics.formulas import Mul

        return Mul(self, other)

    def __truediv__(self, other: "FormulaNode") -> "FormulaNode":
        from libddog.metrics.formulas import Div

        return Div(self, other)
