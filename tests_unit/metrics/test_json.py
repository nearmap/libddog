from libddog.metrics import Query
from libtests.matchers import dict_matcher


def test_exhaustive__with_name() -> None:
    query = (
        Query("aws.ec2.cpuutilization", name="cpu")
        .filter("$az", role="cache")
        .agg("avg")
        .by("az", "role")
        .as_count()
        .rollup("max", 110)
        .fill("last", 112)
    )

    assert query._state.as_dict() == {
        "aggregator": "avg",
        "data_source": "metrics",
        "name": "cpu",
        "query": (
            "avg:aws.ec2.cpuutilization{$az, role:cache} "
            "by {az, role}.as_count().rollup(max, 110).fill(last, 112)"
        ),
    }


def test_minimal__without_name() -> None:
    query1 = Query("aws.ec2.cpuutilization").agg("avg")
    query2 = Query("aws.ec2.memory").agg("max")

    dct1 = query1._state.as_dict()
    dct2 = query2._state.as_dict()

    assert dict_matcher(dct1, name="q1") == {
        "aggregator": "avg",
        "data_source": "metrics",
        "name": "q1",
        "query": "avg:aws.ec2.cpuutilization{*}",
    }

    assert dict_matcher(dct2, name="q2") == {
        "aggregator": "max",
        "data_source": "metrics",
        "name": "q2",
        "query": "max:aws.ec2.memory{*}",
    }

    # generated names are unique for each query
    assert dct1["name"] != dct2["name"]
