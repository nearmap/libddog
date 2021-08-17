import pytest

from libddog.metrics import (
    AggFunc,
    Aggregation,
    As,
    By,
    Fill,
    FillFunc,
    Filter,
    FilterOperator,
    Metric,
    Query,
    QueryState,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
)
from libddog.metrics.query import QueryValidationError

# 'empty' and 'full' states


def test__minimal() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{*}"


def test__exhaustive() -> None:
    # query = QueryState(
    #     metric=Metric(name="aws.ec2.cpuutilization"),
    #     filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
    #     agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
    #     funcs=[
    #         Rollup(func=RollupFunc.MAX, period_s=110),
    #         Fill(func=FillFunc.LAST, limit_s=112),
    #     ],
    # )
    query = Query("aws.ec2.cpuutilization").agg("avg").by("az", "role").as_count()

    # assert query.codegen() == (
    #     "avg:aws.ec2.cpuutilization{$az, role:cache} "
    #     "by {az, role}.as_count().rollup(max, 110).fill(last, 112)"
    # )
    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{*} " "by {az, role}.as_count()"
    )


# aggregation func


def test__invalid_agg_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("weekly")

    assert ctx.value.args[0] == (
        "Aggregation function 'weekly' must be one of 'avg', 'max', 'min', 'sum'"
    )


def test__duplicate_agg_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").agg("avg")

    assert ctx.value.args[0] == (
        "Cannot set aggregation function 'avg' because "
        "query already contains aggregation function 'sum'"
    )


# aggregation by


def test__agg_by_without_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").by("az").agg("sum")

    assert ctx.value.args[0] == (
        "Cannot set aggregation by 'az' because aggregation function is not set yet"
    )


def test__agg_by__multiple_calls() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").by("az").by("role")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{*} by {az, role}"


def test__duplicate_agg_by_is_noop() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").by("az").by("az")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{*} by {az}"


# aggregation as


def test__agg_as_rate() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").as_rate()

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{*}.as_rate()"


def test__agg_as_count_without_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").as_count().agg("sum")

    assert ctx.value.args[0] == (
        "Cannot set as_count() because aggregation function is not set yet"
    )


def test__agg_as_rate_without_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").as_rate().agg("sum")

    assert ctx.value.args[0] == (
        "Cannot set as_rate() because aggregation function is not set yet"
    )
