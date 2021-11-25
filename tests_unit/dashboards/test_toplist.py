from libddog.dashboards import (
    Formula,
    FormulaLimit,
    LimitOrder,
    LiveSpan,
    Position,
    Request,
    Size,
    Time,
    TitleAlign,
    Toplist,
)
from libddog.metrics import Query


def test_toplist__minimal() -> None:
    query = (
        Query("aws.ec2.cpuutilization", name="q1").agg("avg").by("availability-zone")
    )
    cpu = query.identifier()

    toplist = Toplist(
        title="EC2: average CPU utilization per az",
        requests=[
            Request(
                formulas=[
                    Formula(
                        formula=cpu, limit=FormulaLimit(count=10, order=LimitOrder.DESC)
                    )
                ],
                queries=[query],
            )
        ],
    )

    assert toplist.as_dict() == {
        "definition": {
            "requests": [
                {
                    "conditional_formats": [],
                    "formulas": [
                        {"formula": "q1", "limit": {"count": 10, "order": "desc"}}
                    ],
                    "queries": [query._state.as_dict()],
                    "response_format": "scalar",
                }
            ],
            "time": {},
            "title": "EC2: average CPU utilization per az",
            "title_align": "left",
            "title_size": "16",
            "type": "toplist",
        },
        "layout": {"height": 2, "width": 4, "x": 0, "y": 0},
    }


def test_toplist__exhaustive() -> None:
    query = (
        Query("aws.ec2.cpuutilization", name="q1").agg("avg").by("availability-zone")
    )
    cpu = query.identifier()

    toplist = Toplist(
        title="EC2: average CPU utilization per az",
        title_size=11,
        title_align=TitleAlign.LEFT,
        time=Time(live_span=LiveSpan.LAST_5M),
        requests=[
            Request(
                formulas=[
                    Formula(
                        formula=cpu, limit=FormulaLimit(count=10, order=LimitOrder.DESC)
                    )
                ],
                queries=[query],
            )
        ],
        size=Size(height=3, width=6),
        position=Position(x=0, y=4),
    )

    assert toplist.as_dict() == {
        "definition": {
            "requests": [
                {
                    "conditional_formats": [],
                    "formulas": [
                        {"formula": "q1", "limit": {"count": 10, "order": "desc"}}
                    ],
                    "queries": [query._state.as_dict()],
                    "response_format": "scalar",
                }
            ],
            "time": {"live_span": "5m"},
            "title": "EC2: average CPU utilization per az",
            "title_align": "left",
            "title_size": "11",
            "type": "toplist",
        },
        "layout": {"height": 3, "width": 6, "x": 0, "y": 4},
    }
