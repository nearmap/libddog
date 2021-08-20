from libddog.dashboards import (
    Comparator,
    ConditionalFormat,
    ConditionalFormatPalette,
    DisplayType,
    Formula,
    LineType,
    LineWidth,
    Palette,
    Request,
    Style,
)
from libddog.metrics import Query


def test_request__minimal() -> None:
    request = Request(
        queries=[],
    )

    assert request.as_dict() == {
        "conditional_formats": [],
        "display_type": "line",
        "formulas": [],
        "on_right_yaxis": False,
        "queries": [],
        "style": {
            "line_type": "solid",
            "line_width": "normal",
            "palette": "dog_classic",
        },
    }


def test_request__exhaustive() -> None:
    query_cpu = Query("aws.ec2.cpuutilization", name="cpu").agg("avg")
    cpu = query_cpu.identifier()

    request = Request(
        title="cpu usage",
        formulas=[Formula(formula=cpu, alias="cpu")],
        queries=[query_cpu],
        conditional_formats=[
            ConditionalFormat(
                comparator=Comparator.GT,
                value=70,
                palette=ConditionalFormatPalette.WHITE_ON_RED,
            ),
            ConditionalFormat(
                comparator=Comparator.GT,
                value=50,
                palette=ConditionalFormatPalette.WHITE_ON_YELLOW,
            ),
            ConditionalFormat(
                comparator=Comparator.LTE,
                value=50,
                palette=ConditionalFormatPalette.WHITE_ON_GREEN,
            ),
        ],
        display_type=DisplayType.BARS,
        style=Style(
            line_type=LineType.DASHED,
            line_width=LineWidth.THICK,
            palette=Palette.ORANGE,
        ),
        on_right_yaxis=True,
    )

    assert request.as_dict() == {
        "conditional_formats": [
            {"comparator": ">", "palette": "white_on_red", "value": 70},
            {"comparator": ">", "palette": "white_on_yellow", "value": 50},
            {"comparator": "<=", "palette": "white_on_green", "value": 50},
        ],
        "display_type": "bars",
        "formulas": [{"alias": "cpu", "formula": "cpu"}],
        "on_right_yaxis": True,
        "queries": [
            {
                "aggregator": "avg",
                "data_source": "metrics",
                "name": "cpu",
                "query": "avg:aws.ec2.cpuutilization{*}",
            }
        ],
        "style": {"line_type": "dashed", "line_width": "thick", "palette": "orange"},
    }


# corner cases


def test_request__synthesize_formulas_from_queries() -> None:
    reqs = Query("aws.elb.http_requests", name="reqs").agg("avg")
    cpu = Query("aws.ec2.cpuutilization", name="cpu").agg("avg")

    request = Request(
        queries=[reqs, cpu],
    )

    assert request.as_dict() == {
        "conditional_formats": [],
        "display_type": "line",
        "formulas": [{"formula": "reqs"}, {"formula": "cpu"}],
        "on_right_yaxis": False,
        "queries": [
            {
                "aggregator": "avg",
                "data_source": "metrics",
                "name": "reqs",
                "query": "avg:aws.elb.http_requests{*}",
            },
            {
                "aggregator": "avg",
                "data_source": "metrics",
                "name": "cpu",
                "query": "avg:aws.ec2.cpuutilization{*}",
            },
        ],
        "style": {
            "line_type": "solid",
            "line_width": "normal",
            "palette": "dog_classic",
        },
    }
