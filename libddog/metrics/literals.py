from libddog.metrics.bases import QueryNode


class Float(QueryNode):
    def __init__(self, value: float) -> None:
        self.value = value

    def codegen(self) -> str:
        return f"{self.value}"


class Int(QueryNode):
    def __init__(self, value: int) -> None:
        self.value = value

    def codegen(self) -> str:
        return f"{self.value}"


class Str(QueryNode):
    def __init__(self, value: str) -> None:
        self.value = value

    def codegen(self) -> str:
        return self.value
