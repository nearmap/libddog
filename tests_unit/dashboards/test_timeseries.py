from libddog.dashboards import (
    LegendColumn,
    LegendLayout,
    LineMarker,
    MarkerLineStyle,
    MarkerSeverity,
    Position,
    RangeMarker,
    Request,
    Scale,
    Size,
    Timeseries,
    TitleAlign,
    YAxis,
)
from libddog.metrics import Query


def test_timeseries__minimal() -> None:
    query = Query("aws.ec2.cpuutilization", name="q1").agg("avg")

    ts = Timeseries(title="cpu", requests=[Request(queries=[query])])

    assert ts.as_dict() == {
        "definition": {
            "legend_columns": ["avg", "min", "max", "value", "sum"],
            "legend_layout": "auto",
            "markers": [],
            "requests": [
                {
                    "display_type": "line",
                    "formulas": [{"formula": "q1"}],
                    "on_right_yaxis": False,
                    "queries": [
                        {
                            "data_source": "metrics",
                            "name": "q1",
                            "query": "avg:aws.ec2.cpuutilization{*}",
                        }
                    ],
                    "response_format": "timeseries",
                    "style": {
                        "line_type": "solid",
                        "line_width": "normal",
                        "palette": "dog_classic",
                    },
                }
            ],
            "show_legend": True,
            "title": "cpu",
            "title_align": "left",
            "title_size": "16",
            "type": "timeseries",
            "yaxis": {
                "include_zero": True,
                "label": "",
                "max": "auto",
                "min": "auto",
                "scale": "linear",
            },
        },
        "layout": {"height": 2, "width": 4, "x": 0, "y": 0},
    }


def test_timeseries__exhaustive() -> None:
    query = Query("aws.ec2.cpuutilization", name="q1").agg("avg")

    ts = Timeseries(
        title="cpu",
        title_size=17,
        title_align=TitleAlign.LEFT,
        show_legend=False,
        legend_layout=LegendLayout.EXPANDED,
        legend_columns=[LegendColumn.MAX, LegendColumn.MIN],
        requests=[Request(queries=[query])],
        yaxis=YAxis(
            include_zero=False,
            scale=Scale.LOG,
            label="memory",
            min=1,
            max=99,
        ),
        markers=[
            LineMarker(
                value=90,
                label="ok zone threshold",
                severity=MarkerSeverity.OK,
                line_style=MarkerLineStyle.BOLD,
            ),
            RangeMarker(
                lower=95,
                upper=99,
                label="warning zone",
                severity=MarkerSeverity.WARNING,
                line_style=MarkerLineStyle.DASHED,
            ),
        ],
        size=Size(width=1, height=4),
        position=Position(x=2, y=3),
    )

    assert ts.as_dict() == {
        "definition": {
            "legend_columns": ["max", "min"],
            "legend_layout": "vertical",
            "markers": [
                {
                    "display_type": "ok bold",
                    "label": "ok zone threshold",
                    "value": "y = 90",
                },
                {
                    "display_type": "warning dashed",
                    "label": "warning zone",
                    "value": "95 < y < 99",
                },
            ],
            "requests": [
                {
                    "display_type": "line",
                    "formulas": [{"formula": "q1"}],
                    "on_right_yaxis": False,
                    "queries": [
                        {
                            "data_source": "metrics",
                            "name": "q1",
                            "query": "avg:aws.ec2.cpuutilization{*}",
                        }
                    ],
                    "response_format": "timeseries",
                    "style": {
                        "line_type": "solid",
                        "line_width": "normal",
                        "palette": "dog_classic",
                    },
                }
            ],
            "show_legend": False,
            "title": "cpu",
            "title_align": "left",
            "title_size": "17",
            "type": "timeseries",
            "yaxis": {
                "include_zero": False,
                "label": "memory",
                "max": "99",
                "min": "1",
                "scale": "log",
            },
        },
        "layout": {"height": 4, "width": 1, "x": 2, "y": 3},
    }
