from libddog.dashboards import (
    LiveSpan,
    Position,
    QueryValue,
    Request,
    Size,
    Time,
    TitleAlign,
)
from libddog.metrics import Query


def test_query_value__minimal() -> None:
    query = Query("aws.ec2.cpuutilization", name="q1").agg("avg")

    qv = QueryValue(
        title="nodes",
        requests=[Request(queries=[query])],
    )

    assert qv.as_dict() == {
        "definition": {
            "autoscale": True,
            "precision": 2,
            "requests": [
                {
                    "conditional_formats": [],
                    "formulas": [{"formula": "q1"}],
                    "queries": [query._state.as_dict()],
                    "response_format": "scalar",
                }
            ],
            "time": {},
            "title": "nodes",
            "title_align": "left",
            "title_size": "16",
            "type": "query_value",
        },
        "layout": {"height": 2, "width": 2, "x": 0, "y": 0},
    }


def test_query_value__exhaustive() -> None:
    query = Query("aws.ec2.cpuutilization", name="q1").agg("avg")

    qv = QueryValue(
        title="nodes",
        title_size=11,
        title_align=TitleAlign.LEFT,
        time=Time(live_span=LiveSpan.LAST_1D),
        autoscale=False,
        custom_unit="lightyears",
        precision=7,
        requests=[Request(queries=[query])],
        size=Size(width=4, height=1),
        position=Position(x=3, y=2),
    )

    assert qv.as_dict() == {
        "definition": {
            "autoscale": False,
            "custom_unit": "lightyears",
            "precision": 7,
            "requests": [
                {
                    "conditional_formats": [],
                    "formulas": [{"formula": "q1"}],
                    "queries": [query._state.as_dict()],
                    "response_format": "scalar",
                }
            ],
            "time": {"live_span": "1d"},
            "title": "nodes",
            "title_align": "left",
            "title_size": "11",
            "type": "query_value",
        },
        "layout": {"height": 1, "width": 4, "x": 3, "y": 2},
    }
