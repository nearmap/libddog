import pytest

from libddog.common.errors import UnresolvedFormulaIdentifiers
from libddog.dashboards import Formula, Request
from libddog.metrics import AggFunc, Aggregation, Metric, QueryState
from libddog.metrics.literals import Identifier


def test_formula__exhaustive() -> None:
    query_reqs = QueryState(
        metric=Metric(name="aws.elb.http_requests"),
        agg=Aggregation(func=AggFunc.AVG),
        name="reqs",
    )
    query_cpu = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
        name="cpu",
    )

    reqs = query_reqs.identifier()
    cpu = query_cpu.identifier()

    request = Request(
        formulas=[Formula(formula=reqs / cpu, alias="requests per cpu")],
        queries=[query_reqs, query_cpu],
    )

    assert request.as_dict() == {
        "conditional_formats": [],
        "display_type": "line",
        "formulas": [{"alias": "requests per cpu", "formula": "(reqs / cpu)"}],
        "on_right_yaxis": False,
        "queries": [query_reqs.as_dict(), query_cpu.as_dict()],
        "style": {
            "line_type": "solid",
            "line_width": "normal",
            "palette": "dog_classic",
        },
    }


# corner cases


def test_formula__unresolved_identifier() -> None:
    query = QueryState(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
        name="q1",
    )

    q1 = query.identifier()
    q2 = Identifier("q2")  # we just made it up

    request = Request(
        formulas=[
            Formula(
                formula=q1 * q2,
            )
        ],
        queries=[query],
    )

    with pytest.raises(UnresolvedFormulaIdentifiers) as ctx:
        request.as_dict()

    assert ctx.value.args[0] == (
        "identifier(s) 'q2' in the formula '(q1 * q2)' not present in any query"
    )
