import pytest

from libddog.metrics import Query
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


# start with the 'full' state and remove parts, covering most combinations


def test__exhaustive__no_agg() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "aws.ec2.cpuutilization{$az, role:cache}.rollup(max, 110).fill(last, 112)"
    )


def test__exhaustive__no_filter() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{*} "
        "by {az, role}.as_count().rollup(max, 110).fill(last, 112)"
    )


def test__exhaustive__filter_with_tmplvar_only() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az} "
        "by {az, role}.as_count().rollup(max, 110).fill(last, 112)"
    )


def test__exhaustive__agg_with_func_and_by_only() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.rollup(max, 110).fill(last, 112)"
    )


def test__exhaustive__agg_with_func_and_as_only() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .as_count()
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache}"
        ".as_count().rollup(max, 110).fill(last, 112)"
    )


def test__exhaustive__agg_with_func_only() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache}"
        ".rollup(max, 110).fill(last, 112)"
    )


def test__exhaustive__no_rollup() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().fill(last, 112)"
    )


def test__exhaustive__rollup_with_func_only() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .rollup("max")
        .fill("last", 112)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max).fill(last, 112)"
    )


def test__exhaustive__no_fill() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .rollup("max", 110)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max, 110)"
    )


def test__exhaustive__fill_with_func_only() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .rollup("max", 110)
        .fill("last")
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max, 110).fill(last)"
    )


def test__exhaustive__fill_before_rollup() -> None:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .fill("last", 112)
        .rollup("max", 110)
    )

    assert query._state.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().fill(last, 112).rollup(max, 110)"
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


def test__agg_by__pass_tmpl_var_as_tag() -> None:
    with pytest.raises(QueryValidationError) as ctx:
        Query("aws.ec2.cpuutilization").agg("sum").by("$role")

    assert ctx.value.args[0] == (
        "Aggregation by '$role' must be a tag, not a template variable"
    )


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


# character set

VALID_TAG_NAMES = [
    ("upper case", "TAG_NAME"),
    ("mixed case", "tagName"),
    ("dotted name", "looks.like.a.metric.name"),
    ("infix dash", "first-name"),
    ("infix slash", "person/name"),
]

INVALID_TAG_NAMES = [
    ("space", "availability zone"),
    ("wildcard", "regio*"),
    ("starts with digit", "3d"),
    ("wildcard suffix", "us-east-*"),
    ("wildcard prefix", "*-east-1"),
    ("filesystem path", "/dev/null"),
    ("dash terminator", "-secret-"),
    ("key value", "key:value"),
]

VALID_TMPL_VARS = [(case, f"${pattern}") for case, pattern in VALID_TAG_NAMES]
INVALID_TMPL_VARS = [(case, f"${pattern}") for case, pattern in INVALID_TAG_NAMES]

VALID_TAG_VALUES = [
    ("upper case", "TAG_VALUE"),
    ("mixed case", "tagValue"),
    ("starts with digit", "3d"),
    ("wildcard suffix", "us-east-*"),
    ("wildcard prefix", "*-east-1"),
    ("infix slash", "person/name"),
    ("filesystem path", "/dev/null"),
    ("dotted name", "looks.like.a.metric.name"),
    ("infix dash", "first-name"),
    ("dash terminator", "-secret-"),
    # yes, it's valid even though it looks like a tag:tag:value situation
    ("key value", "key:value"),
]

INVALID_TAG_VALUES = [
    ("space", "us east"),
    ("infix wildcard", "us-*-1"),
    ("multiple wildcards", "us-east-**"),
]


def test_charset__tag_name() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    for _, tag_name in VALID_TAG_NAMES:
        query.by(tag_name)  # does not raise
        query.filter(**{tag_name: "value"})  # does not raise
        query.filter_ne(**{tag_name: "value"})  # does not raise

    for _, tag_name in INVALID_TAG_NAMES:
        with pytest.raises(QueryValidationError) as ctx:
            query.by(tag_name)
        assert ctx.value.args[0] == f"Invalid tag name: '{tag_name}'"

        with pytest.raises(QueryValidationError) as ctx:
            query.filter(**{tag_name: "value"})
        assert ctx.value.args[0] == f"Invalid tag name: '{tag_name}'"

        with pytest.raises(QueryValidationError) as ctx:
            query.filter_ne(**{tag_name: "value"})
        assert ctx.value.args[0] == f"Invalid tag name: '{tag_name}'"


def test_charset__tmpl_var() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    for _, tag_name in VALID_TMPL_VARS:
        query.filter(tag_name)  # does not raise
        query.filter_ne(tag_name)  # does not raise

    for _, tag_name in INVALID_TMPL_VARS:
        with pytest.raises(QueryValidationError) as ctx:
            query.filter(tag_name)
        assert ctx.value.args[0] == f"Invalid template variable: '{tag_name}'"

        with pytest.raises(QueryValidationError) as ctx:
            query.filter_ne(tag_name)
        assert ctx.value.args[0] == f"Invalid template variable: '{tag_name}'"


def test_charset__tag_value() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    for _, tag_value in VALID_TAG_VALUES:
        query.filter(region=tag_value)  # does not raise
        query.filter_ne(region=tag_value)  # does not raise

    for _, tag_value in INVALID_TAG_VALUES:
        with pytest.raises(QueryValidationError) as ctx:
            query.filter(region=tag_value)
        assert ctx.value.args[0] == f"Invalid tag value: '{tag_value}'"

        with pytest.raises(QueryValidationError) as ctx:
            query.filter_ne(region=tag_value)
        assert ctx.value.args[0] == f"Invalid tag value: '{tag_value}'"


# internal state


def test_state_is_cloned__agg_func() -> None:
    query = Query("aws.ec2.cpuutilization")

    fst = query.agg("avg")
    snd = query.agg("sum")

    assert fst._state.codegen() == "avg:aws.ec2.cpuutilization{*}"
    assert snd._state.codegen() == "sum:aws.ec2.cpuutilization{*}"


def test_state_is_cloned__agg_by() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    fst = query.by("az")
    snd = query.by("region")

    assert fst._state.codegen() == "avg:aws.ec2.cpuutilization{*} by {az}"
    assert snd._state.codegen() == "avg:aws.ec2.cpuutilization{*} by {region}"


def test_state_is_cloned__agg_as() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    fst = query.as_count()
    snd = query.as_rate()

    assert fst._state.codegen() == "avg:aws.ec2.cpuutilization{*}.as_count()"
    assert snd._state.codegen() == "avg:aws.ec2.cpuutilization{*}.as_rate()"


def test_state_is_cloned__filter() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    fst = query.filter(region="us-east-1")
    snd = query.filter(region="us-west-1")

    assert fst._state.codegen() == "avg:aws.ec2.cpuutilization{region:us-east-1}"
    assert snd._state.codegen() == "avg:aws.ec2.cpuutilization{region:us-west-1}"


def test_state_is_cloned__filter_ne() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    fst = query.filter_ne(region="us-east-1")
    snd = query.filter_ne(region="us-west-1")

    assert fst._state.codegen() == "avg:aws.ec2.cpuutilization{!region:us-east-1}"
    assert snd._state.codegen() == "avg:aws.ec2.cpuutilization{!region:us-west-1}"


def test_state_is_cloned__rollup() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    fst = query.rollup("min")
    snd = query.rollup("max")

    assert fst._state.codegen() == "avg:aws.ec2.cpuutilization{*}.rollup(min)"
    assert snd._state.codegen() == "avg:aws.ec2.cpuutilization{*}.rollup(max)"


def test_state_is_cloned__fill() -> None:
    query = Query("aws.ec2.cpuutilization").agg("avg")

    fst = query.fill("zero")
    snd = query.fill("last")

    assert fst._state.codegen() == "avg:aws.ec2.cpuutilization{*}.fill(zero)"
    assert snd._state.codegen() == "avg:aws.ec2.cpuutilization{*}.fill(last)"
