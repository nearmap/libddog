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
from tests.tools import dict_matcher


def test_exhaustive__with_name() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="az"), Tag(tag="role", value="cache")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
        rollup=Rollup(func=RollupFunc.MAX, period_s=110),
        name="cpu",
    )

    assert query.as_dict() == {
        "aggregator": "avg",
        "data_source": "metrics",
        "name": "cpu",
        "query": (
            "avg:aws.ec2.cpuutilization{$az, role:cache} "
            "by {az, role}.as_count().rollup(max, 110)"
        ),
    }


def test_minimal__without_name() -> None:
    query1 = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
    )
    query2 = Query(
        metric=Metric(name="aws.ec2.memory"),
        agg=Aggregation(func=AggFunc.MAX),
    )

    q1 = query1.as_dict()
    q2 = query2.as_dict()

    assert dict_matcher(q1, name="q1") == {
        "aggregator": "avg",
        "data_source": "metrics",
        "name": "q1",
        "query": "avg:aws.ec2.cpuutilization",
    }

    assert dict_matcher(q2, name="q2") == {
        "aggregator": "max",
        "data_source": "metrics",
        "name": "q2",
        "query": "max:aws.ec2.memory",
    }

    assert q1["name"] != q2["name"]
