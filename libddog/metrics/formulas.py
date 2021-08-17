from libddog.metrics.bases import FormulaNode


class BinaryFormula(FormulaNode):
    symbol: str = ""

    def __init__(self, left: FormulaNode, right: FormulaNode) -> None:
        self.left = left
        self.right = right

    def codegen(self) -> str:
        return f"({self.left.codegen()} {self.symbol} {self.right.codegen()})"


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

    def codegen(self) -> str:
        return f"{self.left.codegen()}{self.symbol} {self.right.codegen()}"
