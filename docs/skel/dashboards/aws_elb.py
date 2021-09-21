from dashboards.shared import get_region_tmpl_var_presets

from libddog.dashboards import (
    Dashboard,
    DisplayType,
    Position,
    Request,
    Size,
    Timeseries,
    Widget,
)
from libddog.metrics import Query


def get_reqs_per_elb() -> Widget:
    query = (
        Query("aws.elb.request_count")
        .filter("$region")
        .agg("sum")
        .by("availability-zone")
        .as_count()
        .rollup("sum", 5 * 60)
    )

    widget = Timeseries(
        title="ELB: total requests by AZ every 5min",
        requests=[
            Request(
                queries=[query],
                display_type=DisplayType.BARS,
            ),
        ],
        size=Size(height=3, width=5),
        position=Position(x=0, y=0),
    )

    return widget


def get_dashboard() -> Dashboard:
    reqs_per_az = get_reqs_per_elb()

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog skel: AWS ELB dashboard",
        desc="Sample dashboard showing metrics from ELB",
        widgets=[reqs_per_az],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
