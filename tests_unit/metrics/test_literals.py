from libddog.metrics import Float, Identifier, Int


def test_float() -> None:
    lit = Float(2.1)
    assert lit.codegen() == "2.1"


def test_int() -> None:
    lit = Int(7)
    assert lit.codegen() == "7"


def test_identifier() -> None:
    lit = Identifier("q1")
    assert lit.codegen() == "q1"
