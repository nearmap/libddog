import pytest

from libddog.common.errors import UnresolvedFormulaIdentifiers
from libddog.dashboards import Formula, Request
from libddog.metrics import AggFunc, Aggregation, Metric, Query


def test_formula__exhaustive() -> None:
    reqs = Query(
        metric=Metric(name="aws.elb.http_requests"),
        agg=Aggregation(func=AggFunc.AVG),
        name="reqs",
    )
    cpu = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
        name="cpu",
    )

    request = Request(
        formulas=[Formula(text="reqs / cpu", alias="requests per cpu")],
        queries=[reqs, cpu],
    )

    assert request.as_dict() == {
        "conditional_formats": [],
        "display_type": "line",
        "formulas": [{"alias": "requests per cpu", "formula": "reqs / cpu"}],
        "on_right_yaxis": False,
        "queries": [reqs.as_dict(), cpu.as_dict()],
        "style": {
            "line_type": "solid",
            "line_width": "normal",
            "palette": "dog_classic",
        },
    }


# corner cases


def _test_formula__unresolved_var() -> None:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
        name="q1",
    )

    request = Request(
        formulas=[
            Formula(
                text="q1 * q2",
            )
        ],
        queries=[query],
    )

    with pytest.raises(UnresolvedFormulaIdentifiers) as ctx:
        request.as_dict()

    assert ctx.value.args[0] == (
        "identifier(s) {'q2'} in the formula 'q1 * q2' not present in any query"
    )
