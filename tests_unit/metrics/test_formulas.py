from libddog.metrics import Add, Comma, Div, Identifier, Mul, Paren, Sub

# trivial cases


def test_paren__minimal() -> None:
    formula = Paren(Identifier("q1"))

    assert formula.codegen() == "(q1)"


def test_add__minimal() -> None:
    formula = Add(Identifier("q1"), Identifier("q2"))

    assert formula.codegen() == "(q1 + q2)"


def test_sub__minimal() -> None:
    formula = Sub(Identifier("q1"), Identifier("q2"))

    assert formula.codegen() == "(q1 - q2)"


def test_mul__minimal() -> None:
    formula = Mul(Identifier("q1"), Identifier("q2"))

    assert formula.codegen() == "(q1 * q2)"


def test_div__minimal() -> None:
    formula = Div(Identifier("q1"), Identifier("q2"))

    assert formula.codegen() == "(q1 / q2)"


def test_comma__minimal() -> None:
    formula = Comma(Identifier("q1"), Identifier("q2"))

    assert formula.codegen() == "q1, q2"


# infix operators


def test_add__infix() -> None:
    formula = Identifier("q1") + Identifier("q2")

    assert formula.codegen() == "(q1 + q2)"


def test_sub__infix() -> None:
    formula = Identifier("q1") - Identifier("q2")

    assert formula.codegen() == "(q1 - q2)"


def test_mul__infix() -> None:
    formula = Identifier("q1") * Identifier("q2")

    assert formula.codegen() == "(q1 * q2)"


def test_div__infix() -> None:
    formula = Identifier("q1") / Identifier("q2")

    assert formula.codegen() == "(q1 / q2)"
