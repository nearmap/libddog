from dashboards.shared import get_region_tmpl_var_presets

from libddog.dashboards import (
    Dashboard,
    DisplayType,
    LineType,
    LineWidth,
    Position,
    Request,
    Size,
    Style,
    Timeseries,
    Widget,
)
from libddog.metrics import Query


def get_cpu_per_az() -> Widget:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$region")
        .agg("avg")
        .by("availability-zone")
    )

    widget = Timeseries(
        title="EC2: average CPU utilization per az",
        requests=[
            Request(
                queries=[query],
                display_type=DisplayType.AREAS,
                style=Style(
                    line_type=LineType.DASHED,
                    line_width=LineWidth.THIN,
                ),
            ),
        ],
        size=Size(height=2, width=3),
        position=Position(x=0, y=0),
    )

    return widget


def get_dashboard() -> Dashboard:
    cpu_per_az = get_cpu_per_az()

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog skel: AWS EC2 dashboard",
        desc="Sample dashboard showing metrics from EC2",
        widgets=[cpu_per_az],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
