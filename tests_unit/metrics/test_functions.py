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
    Int,
    Metric,
    Paren,
    Query,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
    abs,
)


def test_abs() -> None:
    query = abs(
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            agg=Aggregation(func=AggFunc.AVG),
        )
    )

    assert query.codegen() == "abs(avg:aws.ec2.cpuutilization{*})"


def test_add() -> None:
    left = abs(
        Query(
            metric=Metric(name="aws.ec2.cpu"),
            agg=Aggregation(func=AggFunc.AVG),
        )
    )
    right = abs(
        Query(
            metric=Metric(name="aws.ec2.memory"),
            agg=Aggregation(func=AggFunc.AVG),
        )
    )
    query = Add(left, right)

    assert query.codegen() == "abs(avg:aws.ec2.cpu{*}) + abs(avg:aws.ec2.memory{*})"


def test_paren() -> None:
    left = abs(
        Query(
            metric=Metric(name="aws.ec2.cpu"),
            agg=Aggregation(func=AggFunc.AVG),
        )
    )
    right = abs(
        Query(
            metric=Metric(name="aws.ec2.memory"),
            agg=Aggregation(func=AggFunc.AVG),
        )
    )
    paren = Paren(Add(left, right))
    query = Add(paren, Int(1))

    assert query.codegen() == (
        "(abs(avg:aws.ec2.cpu{*}) + abs(avg:aws.ec2.memory{*})) + 1"
    )
