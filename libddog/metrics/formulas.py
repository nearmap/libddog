from libddog.metrics.bases import QueryNode


class Paren(QueryNode):
    def __init__(self, expr: QueryNode) -> None:
        self.expr = expr

    def codegen(self) -> str:
        return f"({self.expr.codegen()})"


class BinaryFormula(QueryNode):
    symbol: str = ""

    def __init__(self, left: QueryNode, right: QueryNode) -> None:
        self.left = left
        self.right = right

    def codegen(self) -> str:
        return f"{self.left.codegen()} {self.symbol} {self.right.codegen()}"


class Add(BinaryFormula):
    symbol = "+"


class Sub(BinaryFormula):
    symbol = "-"


class Mul(BinaryFormula):
    symbol = "*"


class Div(BinaryFormula):
    symbol = "/"


class Comma(BinaryFormula):
    symbol = ","
