import pytest

from libddog.metrics import (
    Add,
    AggFunc,
    Aggregation,
    As,
    By,
    Fill,
    FillFunc,
    Filter,
    FilterOperator,
    Identifier,
    Int,
    Metric,
    Paren,
    Query,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
    abs,
    autosmooth,
    cumsum,
    day_before,
    default_zero,
    derivative,
    diff,
    dt,
    ewma_3,
    ewma_5,
    ewma_10,
    ewma_20,
    hour_before,
    integral,
    log2,
    log10,
    median_3,
    median_5,
    median_7,
    median_9,
    monotonic_diff,
    month_before,
    per_hour,
    per_minute,
    per_second,
    timeshift,
    week_before,
)
from libddog.metrics.exceptions import FormulaValidationError

# def test_abs() -> None:
#     query = abs(
#         Query(
#             metric=Metric(name="aws.ec2.cpuutilization"),
#             agg=Aggregation(func=AggFunc.AVG),
#         )
#     )

#     assert query.codegen() == "abs(avg:aws.ec2.cpuutilization{*})"


# def test_add() -> None:
#     left = abs(
#         Query(
#             metric=Metric(name="aws.ec2.cpu"),
#             agg=Aggregation(func=AggFunc.AVG),
#         )
#     )
#     right = abs(
#         Query(
#             metric=Metric(name="aws.ec2.memory"),
#             agg=Aggregation(func=AggFunc.AVG),
#         )
#     )
#     query = Add(left, right)

#     assert query.codegen() == "abs(avg:aws.ec2.cpu{*}) + abs(avg:aws.ec2.memory{*})"


# def test_paren() -> None:
#     left = abs(
#         Query(
#             metric=Metric(name="aws.ec2.cpu"),
#             agg=Aggregation(func=AggFunc.AVG),
#         )
#     )
#     right = abs(
#         Query(
#             metric=Metric(name="aws.ec2.memory"),
#             agg=Aggregation(func=AggFunc.AVG),
#         )
#     )
#     paren = Paren(Add(left, right))
#     query = Add(paren, Int(1))

#     assert query.codegen() == (
#         "(abs(avg:aws.ec2.cpu{*}) + abs(avg:aws.ec2.memory{*})) + 1"
#     )


# arithmetic


def test_abs__minimal() -> None:
    cpu = Identifier("cpu")
    formula = abs(cpu)

    assert formula.codegen() == "abs(cpu)"


def test_log2__minimal() -> None:
    cpu = Identifier("cpu")
    formula = log2(cpu)

    assert formula.codegen() == "log2(cpu)"


def test_log10__minimal() -> None:
    cpu = Identifier("cpu")
    formula = log10(cpu)

    assert formula.codegen() == "log10(cpu)"


def test_cumsum__minimal() -> None:
    cpu = Identifier("cpu")
    formula = cumsum(cpu)

    assert formula.codegen() == "cumsum(cpu)"


def test_integral__minimal() -> None:
    cpu = Identifier("cpu")
    formula = integral(cpu)

    assert formula.codegen() == "integral(cpu)"


# interpolation


def test_default_zero__minimal() -> None:
    cpu = Identifier("cpu")
    formula = default_zero(cpu)

    assert formula.codegen() == "default_zero(cpu)"


# timeshift


def test_hour_before__minimal() -> None:
    cpu = Identifier("cpu")
    formula = hour_before(cpu)

    assert formula.codegen() == "hour_before(cpu)"


def test_day_before__minimal() -> None:
    cpu = Identifier("cpu")
    formula = day_before(cpu)

    assert formula.codegen() == "day_before(cpu)"


def test_week_before__minimal() -> None:
    cpu = Identifier("cpu")
    formula = week_before(cpu)

    assert formula.codegen() == "week_before(cpu)"


def test_month_before__minimal() -> None:
    cpu = Identifier("cpu")
    formula = month_before(cpu)

    assert formula.codegen() == "month_before(cpu)"


def test_timeshift__minimal() -> None:
    cpu = Identifier("cpu")
    formula = timeshift(cpu, -3600)

    assert formula.codegen() == "timeshift(cpu, -3600)"


def test_timeshift__non_negative_time() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        timeshift(cpu, 0)

    assert ctx.value.args[0] == "timeshift interval must be below zero: 0"


# rate


def test_per_second__minimal() -> None:
    cpu = Identifier("cpu")
    formula = per_second(cpu)

    assert formula.codegen() == "per_second(cpu)"


def test_per_minute__minimal() -> None:
    cpu = Identifier("cpu")
    formula = per_minute(cpu)

    assert formula.codegen() == "per_minute(cpu)"


def test_per_hour__minimal() -> None:
    cpu = Identifier("cpu")
    formula = per_hour(cpu)

    assert formula.codegen() == "per_hour(cpu)"


def test_dt__minimal() -> None:
    cpu = Identifier("cpu")
    formula = dt(cpu)

    assert formula.codegen() == "dt(cpu)"


def test_diff__minimal() -> None:
    cpu = Identifier("cpu")
    formula = diff(cpu)

    assert formula.codegen() == "diff(cpu)"


def test_monotonic_diff__minimal() -> None:
    cpu = Identifier("cpu")
    formula = monotonic_diff(cpu)

    assert formula.codegen() == "monotonic_diff(cpu)"


def test_derivative__minimal() -> None:
    cpu = Identifier("cpu")
    formula = derivative(cpu)

    assert formula.codegen() == "derivative(cpu)"


# smoothing


def test_autosmooth__minimal() -> None:
    cpu = Identifier("cpu")
    formula = autosmooth(cpu)

    assert formula.codegen() == "autosmooth(cpu)"


def test_ewma_3__minimal() -> None:
    cpu = Identifier("cpu")
    formula = ewma_3(cpu)

    assert formula.codegen() == "ewma_3(cpu)"


def test_ewma_5__minimal() -> None:
    cpu = Identifier("cpu")
    formula = ewma_5(cpu)

    assert formula.codegen() == "ewma_5(cpu)"


def test_ewma_10__minimal() -> None:
    cpu = Identifier("cpu")
    formula = ewma_10(cpu)

    assert formula.codegen() == "ewma_10(cpu)"


def test_ewma_20__minimal() -> None:
    cpu = Identifier("cpu")
    formula = ewma_20(cpu)

    assert formula.codegen() == "ewma_20(cpu)"


def test_median_3__minimal() -> None:
    cpu = Identifier("cpu")
    formula = median_3(cpu)

    assert formula.codegen() == "median_3(cpu)"


def test_median_5__minimal() -> None:
    cpu = Identifier("cpu")
    formula = median_5(cpu)

    assert formula.codegen() == "median_5(cpu)"


def test_median_7__minimal() -> None:
    cpu = Identifier("cpu")
    formula = median_7(cpu)

    assert formula.codegen() == "median_7(cpu)"


def test_median_9__minimal() -> None:
    cpu = Identifier("cpu")
    formula = median_9(cpu)

    assert formula.codegen() == "median_9(cpu)"
