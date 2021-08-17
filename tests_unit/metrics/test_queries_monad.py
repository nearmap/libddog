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
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max, 110).fill(last, 112)"
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


# filter


def test__filter__pass_tag_as_tmpl_var() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").filter("role")

    assert ctx.value.args[0] == (
        "Filter key 'role' without value must be a template variable, not a tag"
    )


def test__filter__pass_tmpl_var_as_tag() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").filter(**{"$role": "cache"})

    assert ctx.value.args[0] == (
        "Filter '$role:cache' must be a tag, not a template variable"
    )


def test__filter__multiple_calls_using_tmpl_vars() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").filter("$region").filter("$az")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{$region, $az}"


def test__filter__multiple_calls_using_tags() -> None:
    query = (
        Query("aws.ec2.cpuutilization").agg("avg").filter(role="cache").filter(az="*a")
    )

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{role:cache, az:*a}"


def test__filter__multiple_calls_intermixed() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .agg("avg")
        .filter("$region")
        .filter(role="cache")
        .filter("$az")
        .filter(host="i-123")
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$region, role:cache, $az, host:i-123}"
    )


def test__duplicate_filter_is_noop__using_tmpl_var() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").filter("$az").filter("$az")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{$az}"


def test__duplicate_filter_is_noop__using_tag() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").filter(az="*a").filter(az="*a")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{az:*a}"


def test__conflicting_values_for_same_tag_is_allowed() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").filter(az="*a").filter(az="*b")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{az:*a, az:*b}"


# filter_ne


def test__negating_filter__representative() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .agg("avg")
        .filter_ne("$az")
        .filter_ne(role="cache")
    )

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{!$az, !role:cache}"


def test__negating_filter__pass_tag_as_tmpl_var() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").filter_ne("role")

    assert ctx.value.args[0] == (
        "Filter key 'role' without value must be a template variable, not a tag"
    )


def test__negating_filter__pass_tmpl_var_as_tag() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").filter(**{"$role": "cache"})

    assert ctx.value.args[0] == (
        "Filter '$role:cache' must be a tag, not a template variable"
    )


def test__negating_filter__multiple_calls_using_tmpl_vars() -> None:
    query = (
        Query("aws.ec2.cpuutilization").agg("avg").filter_ne("$region").filter_ne("$az")
    )

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{!$region, !$az}"


def test__negating_filter__multiple_calls_using_tags() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .agg("avg")
        .filter_ne(role="cache")
        .filter_ne(az="*a")
    )

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{!role:cache, !az:*a}"


def test__negating_filter__multiple_calls_intermixed() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .agg("avg")
        .filter_ne("$region")
        .filter_ne(role="cache")
        .filter_ne("$az")
        .filter_ne(host="i-123")
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{!$region, !role:cache, !$az, !host:i-123}"
    )


def test__duplicate_negating_filter_is_noop__using_tmpl_var() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg").filter_ne("$az").filter_ne("$az")

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{!$az}"


def test__duplicate_negating_filter_is_noop__using_tag() -> None:
    query = (
        Query("aws.ec2.cpuutilization").agg("avg").filter_ne(az="*a").filter_ne(az="*a")
    )

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{!az:*a}"


def test__conflicting_negating_values_for_same_tag_is_allowed() -> None:
    query = (
        Query("aws.ec2.cpuutilization").agg("avg").filter_ne(az="*a").filter_ne(az="*b")
    )

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{!az:*a, !az:*b}"


# filter and filter_ne


def test__selecting_and_negating_same_tag_is_allowed() -> None:
    query = (
        Query("aws.ec2.cpuutilization").agg("avg").filter(az="*a").filter_ne(az="*a")
    )

    assert query._state.codegen() == "avg:aws.ec2.cpuutilization{az:*a, !az:*a}"


# rollup


def test__invalid_rollup_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("avg").rollup("tires")

    assert ctx.value.args[0] == (
        "Rollup function 'tires' must be one of 'avg', 'count', 'max', 'min', 'sum'"
    )


def test__duplicate_rollup_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").rollup("min").rollup("count")

    assert ctx.value.args[0] == (
        "Cannot set rollup function 'count' because "
        "query already contains rollup function 'min'"
    )


# fill


def test__invalid_fill_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("avg").fill("bottle")

    assert ctx.value.args[0] == (
        "Fill function 'bottle' must be one of 'last', 'linear', 'null', 'zero'"
    )


def test__duplicate_fill_func() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").fill("last").fill("zero")

    assert ctx.value.args[0] == (
        "Cannot set fill function 'zero' because "
        "query already contains fill function 'last'"
    )
