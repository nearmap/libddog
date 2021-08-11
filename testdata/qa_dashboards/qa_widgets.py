from typing import List

from libddog.dashboards import (
    Dashboard,
    DisplayType,
    LegendColumn,
    LegendLayout,
    LineMarker,
    LineType,
    LineWidth,
    MarkerSeverity,
    Palette,
    PopulatedTemplateVariable,
    Position,
    RangeMarker,
    Request,
    Scale,
    Size,
    Style,
    TemplateVariableDefinition,
    TemplateVariablesPreset,
    Timeseries,
    YAxis,
)
from libddog.dashboards.components import RangeMarker
from libddog.metrics import (
    AggFunc,
    Aggregation,
    By,
    Fill,
    FillFunc,
    Filter,
    Metric,
    Query,
    Rollup,
    RollupFunc,
    TmplVar,
)


def get_region_tmpl_var_presets() -> List[TemplateVariablesPreset]:
    presets = []
    popular_regions = ["ap-southeast-2", "us-east-1", "us-west-1"]

    defn = TemplateVariableDefinition(
        name="region",
        tag="region",
        default_value="us-east-1",
    )

    for region in popular_regions:
        preset = TemplateVariablesPreset(
            name=region,
            populated_vars=[
                PopulatedTemplateVariable(
                    tmpl_var=defn,
                    value=region,
                )
            ],
        )
        presets.append(preset)

    return presets


def get_dashboard() -> Dashboard:
    query_ec2_cpu = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["availability-zone"])),
        funcs=[Fill(func=FillFunc.LINEAR), Rollup(func=RollupFunc.AVG, period_s=60)],
    )

    # Exercises most of the properties of a Timeseries
    wid_ec2_cpu = Timeseries(
        title="EC2: average CPU utilization per az",
        size=Size(height=4, width=6),
        pos=Position(x=0, y=0),
        requests=[
            Request(
                queries=[query_ec2_cpu],
                display_type=DisplayType.AREAS,
                style=Style(
                    line_type=LineType.DASHED,
                    line_width=LineWidth.THIN,
                    palette=Palette.PURPLE,
                ),
            ),
        ],
        yaxis=YAxis(min=0, max=100, scale=Scale.LINEAR),
        markers=[
            LineMarker(value=60, label="60%", severity=MarkerSeverity.WARNING),
            RangeMarker(
                lower=80, upper=100, label="80%", severity=MarkerSeverity.ERROR
            ),
        ],
        legend_layout=LegendLayout.EXPANDED,
        legend_columns=[LegendColumn.AVG, LegendColumn.MAX, LegendColumn.VALUE],
    )

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog QA: exercise widgets",
        desc=(
            "This dashboard is used exclusively for the purposes of integration "
            "testing **libddog**, which a Datadog automation tool.\n\n"
            "It is used during automated test runs as well as for manual (visual) "
            "inspection that everything looks correct.\n\n"
            "[libddog on github](https://github.com/nearmap/libddog)"
        ),
        widgets=[wid_ec2_cpu],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
