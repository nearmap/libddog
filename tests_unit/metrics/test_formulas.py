from libddog.metrics import (
    Add,
    Comma,
    Div,
    Float,
    Identifier,
    Int,
    Mul,
    Sub,
    abs,
    log2,
    log10,
    timeshift,
)

# trivial cases


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


# compound expressions


def test_operator_precedence() -> None:
    formula = (Float(2.1) + Int(4)) / Int(6)

    assert formula.codegen() == ("((2.1 + 4) / 6)")


def test_all_arithmetic_operators() -> None:
    cpu = Identifier("cpu")
    reqs = Identifier("reqs")

    formula = ((abs(cpu) * Int(2)) - reqs) + (log2(cpu) / timeshift(reqs, -3600))

    assert formula.codegen() == (
        "(((abs(cpu) * 2) - reqs) + (log2(cpu) / timeshift(reqs, -3600)))"
    )


def test_nested_function_application() -> None:
    cpu = Identifier("cpu")

    formula = log2(abs(cpu))

    assert formula.codegen() == "log2(abs(cpu))"


def test_function_applied_to_formula() -> None:
    cpu = Identifier("cpu")
    reqs = Identifier("reqs")

    formula = log2(abs(cpu) / log10(reqs))

    assert formula.codegen() == "log2((abs(cpu) / log10(reqs)))"
