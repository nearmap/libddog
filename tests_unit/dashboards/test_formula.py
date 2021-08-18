import pytest

from libddog.common.errors import UnresolvedFormulaIdentifiers
from libddog.dashboards import Formula, Request
from libddog.metrics import Query
from libddog.metrics.literals import Identifier


def test_formula__exhaustive() -> None:
    query_reqs = Query("aws.elb.http_requests", name="reqs").agg("avg")
    query_cpu = Query("aws.ec2.cpuutilization", name="cpu").agg("avg")

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
        "queries": [query_reqs._state.as_dict(), query_cpu._state.as_dict()],
        "style": {
            "line_type": "solid",
            "line_width": "normal",
            "palette": "dog_classic",
        },
    }


# corner cases


def test_formula__unresolved_identifier() -> None:
    query = Query("aws.ec2.cpuutilization", name="q1").agg("avg")

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
