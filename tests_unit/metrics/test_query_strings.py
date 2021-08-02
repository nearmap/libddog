from libddog.metrics import (
    AggFunc,
    Aggregation,
    As,
    By,
    Filter,
    Metric,
    Query,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
)

# 'empty' and 'full' states


def test__minimal() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
    )

    assert query.codegen() == "avg:aws.ec2.cpuutilization"


def test__exhaustive() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        rollup=Rollup(func=RollupFunc.MAX, period_s=110),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max, 110)"
    )


# start with the 'full' state and remove parts, covering most combinations


def test__exhaustive__no_filter() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        rollup=Rollup(func=RollupFunc.MAX, period_s=110),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization by {az, role}.as_count().rollup(max, 110)"
    )


def test__exhaustive__filter_with_tmplvar_only() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        rollup=Rollup(func=RollupFunc.MAX, period_s=110),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az} by {az, role}.as_count().rollup(max, 110)"
    )


def test__exhaustive__agg_with_func_and_by_only() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"])),
        rollup=Rollup(func=RollupFunc.MAX, period_s=110),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} by {az, role}.rollup(max, 110)"
    )


def test__exhaustive__agg_with_func_and_as_only() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, as_=As.COUNT),
        rollup=Rollup(func=RollupFunc.MAX, period_s=110),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache}.as_count().rollup(max, 110)"
    )


def test__exhaustive__agg_with_func_only() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG),
        rollup=Rollup(func=RollupFunc.MAX, period_s=110),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache}.rollup(max, 110)"
    )


def test__exhaustive__no_rollup() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} by {az, role}.as_count()"
    )


def test__exhaustive__rollup_with_func_only() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        rollup=Rollup(func=RollupFunc.MAX),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max)"
    )


# selected corner cases


def test_rollup_default_func() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
        rollup=Rollup(func=RollupFunc.DEFAULT),
    )

    assert query.codegen() == "avg:aws.ec2.cpuutilization"
