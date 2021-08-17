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
    QueryState,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
)
from libddog.metrics.query import Query

# 'empty' and 'full' states


def test__minimal() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
    )

    assert query.codegen() == "avg:aws.ec2.cpuutilization{*}"


def test__exhaustive() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        funcs=[
            Rollup(func=RollupFunc.MAX, period_s=110),
            Fill(func=FillFunc.LAST, limit_s=112),
        ],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max, 110).fill(last, 112)"
    )


# start with the 'full' state and remove parts, covering most combinations


def test__exhaustive__no_agg() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110)],
    )

    assert query.codegen() == ("aws.ec2.cpuutilization{*}.rollup(max, 110)")


def test__exhaustive__no_filter() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{*} by {az, role}.as_count().rollup(max, 110)"
    )


def test__exhaustive__filter_with_tmplvar_only() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az} by {az, role}.as_count().rollup(max, 110)"
    )


def test__exhaustive__agg_with_func_and_by_only() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"])),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} by {az, role}.rollup(max, 110)"
    )


def test__exhaustive__agg_with_func_and_as_only() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, as_=As.COUNT),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache}.as_count().rollup(max, 110)"
    )


def test__exhaustive__agg_with_func_only() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache}.rollup(max, 110)"
    )


def test__exhaustive__no_rollup() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} by {az, role}.as_count()"
    )


def test__exhaustive__rollup_with_func_only() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        funcs=[Rollup(func=RollupFunc.MAX)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max)"
    )


def test__exhaustive__no_fill() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max, 110)"
    )


def test__exhaustive__fill_with_func_only() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        funcs=[Rollup(func=RollupFunc.MAX, period_s=110), Fill(func=FillFunc.LAST)],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().rollup(max, 110).fill(last)"
    )


def test__exhaustive__fill_before_rollup() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        funcs=[
            Fill(func=FillFunc.LAST, limit_s=112),
            Rollup(func=RollupFunc.MAX, period_s=110),
        ],
    )

    assert query.codegen() == (
        "avg:aws.ec2.cpuutilization{$az, role:cache} "
        "by {az, role}.as_count().fill(last, 112).rollup(max, 110)"
    )


# selected corner cases


def test_filter_negating() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(
            conds=[
                TmplVar(tvar="az"),
                Tag(tag="role", value="cache", operator=FilterOperator.NOT_EQUAL),
            ]
        ),
        agg=Aggregation(func=AggFunc.AVG),
    )

    assert query.codegen() == "avg:aws.ec2.cpuutilization{$az, !role:cache}"


def test_rollup_default_func() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
        funcs=[Rollup(func=RollupFunc.DEFAULT)],
    )

    assert query.codegen() == "avg:aws.ec2.cpuutilization{*}"
