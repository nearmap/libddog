from libddog.metrics.bases import FormulaNode


class Float(FormulaNode):
    def __init__(self, value: float) -> None:
        self.value = value

    def codegen(self) -> str:
        return f"{self.value}"


class Int(FormulaNode):
    def __init__(self, value: int) -> None:
        self.value = value

    def codegen(self) -> str:
        return f"{self.value}"


class Identifier(FormulaNode):
    def __init__(self, name: str) -> None:
        self.name = name

    def codegen(self) -> str:
        return f"{self.name}"
