import pytest

from libddog.metrics import (
    Identifier,
    abs,
    anomalies,
    autosmooth,
    clamp_max,
    clamp_min,
    count_nonzero,
    count_not_null,
    cumsum,
    cutoff_max,
    cutoff_min,
    day_before,
    default_zero,
    derivative,
    diff,
    dt,
    ewma_3,
    ewma_5,
    ewma_10,
    ewma_20,
    exclude_null,
    forecast,
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
    moving_rollup,
    outliers,
    per_hour,
    per_minute,
    per_second,
    piecewise_constant,
    robust_trend,
    timeshift,
    top,
    trend_line,
    week_before,
)
from libddog.metrics.exceptions import FormulaValidationError

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


# rollup


def test_moving_rollup__minimal() -> None:
    cpu = Identifier("cpu")
    formula = moving_rollup(cpu, 60, "avg")

    assert formula.codegen() == "moving_rollup(cpu, 60, 'avg')"


def test_moving_rollup__invalid_method() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        moving_rollup(cpu, 60, "using-elephants")

    assert ctx.value.args[0] == (
        "moving_rollup method 'using-elephants' must be one of: "
        "'avg', 'count', 'max', 'min', 'sum'"
    )


# rank


def test_top__minimal() -> None:
    cpu = Identifier("cpu")
    formula = top(cpu, 5, "sum", "asc")

    assert formula.codegen() == "top(cpu, 5, 'sum', 'asc')"


def test_top__out_of_range() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        top(cpu, 6, "sum", "asc")

    assert ctx.value.args[0] == "top limit_to 6 must be one of: 5, 10, 25, 50, 100"


def test_top__invalid_by() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        top(cpu, 5, "unicycle", "asc")

    assert ctx.value.args[0] == (
        "top by 'unicycle' must be one of: "
        "'area', 'l2norm', 'last', 'max', 'mean', 'min', 'sum'"
    )


def test_top__invalid_dir() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        top(cpu, 5, "sum", "sideways")

    assert ctx.value.args[0] == "top dir 'sideways' must be one of: 'asc', 'desc'"


# count


def test_count_nonzero__minimal() -> None:
    cpu = Identifier("cpu")
    formula = count_nonzero(cpu)

    assert formula.codegen() == "count_nonzero(cpu)"


def test_count_not_null__minimal() -> None:
    cpu = Identifier("cpu")
    formula = count_not_null(cpu)

    assert formula.codegen() == "count_not_null(cpu)"


# regression


def test_robust_trend__minimal() -> None:
    cpu = Identifier("cpu")
    formula = robust_trend(cpu)

    assert formula.codegen() == "robust_trend(cpu)"


def test_trend_line__minimal() -> None:
    cpu = Identifier("cpu")
    formula = trend_line(cpu)

    assert formula.codegen() == "trend_line(cpu)"


def test_piecewise_constant__minimal() -> None:
    cpu = Identifier("cpu")
    formula = piecewise_constant(cpu)

    assert formula.codegen() == "piecewise_constant(cpu)"


# algorithms


def test_outliers__dbscan() -> None:
    cpu = Identifier("cpu")
    formula = outliers(cpu, "DBSCAN", 2.0)

    assert formula.codegen() == "outliers(cpu, 'DBSCAN', 2.0)"


def test_outliers__mad() -> None:
    cpu = Identifier("cpu")
    formula = outliers(cpu, "MAD", 3.0, 90)

    assert formula.codegen() == "outliers(cpu, 'MAD', 3.0, 90)"


def test_outliers__invalid_algorithm() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        outliers(cpu, "veryMAD", 2.0)

    assert ctx.value.args[0] == (
        "outliers algorithm 'veryMAD' must be one of: "
        "'DBSCAN', 'MAD', 'scaledDBSCAN', 'scaledMAD'"
    )


def test_outliers__invalid_pct() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        outliers(cpu, "DBSCAN", 2.0, 90)

    assert ctx.value.args[0] == (
        "outliers pct only valid for algorithms: 'MAD', 'scaledMAD'"
    )


def test_anomalies__minimal() -> None:
    cpu = Identifier("cpu")
    formula = anomalies(cpu, "agile", 2)

    assert formula.codegen() == "anomalies(cpu, 'agile', 2)"


def test_anomalies__invalid_algorithm() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        anomalies(cpu, "black-cat", 2)

    assert ctx.value.args[0] == (
        "anomalies algorithm 'black-cat' must be one of: 'agile', 'basic', 'robust'"
    )


def test_forecast__minimal() -> None:
    cpu = Identifier("cpu")
    formula = forecast(cpu, "linear", 2)

    assert formula.codegen() == "forecast(cpu, 'linear', 2)"


def test_forecast__invalid_algorithm() -> None:
    cpu = Identifier("cpu")

    with pytest.raises(FormulaValidationError) as ctx:
        forecast(cpu, "modernist", 2)

    assert ctx.value.args[0] == (
        "forecast algorithm 'modernist' must be one of: 'linear', 'seasonal'"
    )


# exclusion


def test_exclude_null__minimal() -> None:
    cpu = Identifier("cpu")
    formula = exclude_null(cpu, "region")

    assert formula.codegen() == "exclude_null(cpu, 'region')"


def test_cutoff_max__minimal() -> None:
    cpu = Identifier("cpu")
    formula = cutoff_max(cpu, 80)

    assert formula.codegen() == "cutoff_max(cpu, 80)"


def test_cutoff_min__minimal() -> None:
    cpu = Identifier("cpu")
    formula = cutoff_min(cpu, 10)

    assert formula.codegen() == "cutoff_min(cpu, 10)"


def test_clamp_max__minimal() -> None:
    cpu = Identifier("cpu")
    formula = clamp_max(cpu, 70)

    assert formula.codegen() == "clamp_max(cpu, 70)"


def test_clamp_min__minimal() -> None:
    cpu = Identifier("cpu")
    formula = clamp_min(cpu, 15)

    assert formula.codegen() == "clamp_min(cpu, 15)"
