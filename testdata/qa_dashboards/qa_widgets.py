from typing import List

from libddog.dashboards import (
    BackgroundColor,
    Comparator,
    ConditionalFormat,
    ConditionalFormatPalette,
    Dashboard,
    DisplayType,
    Formula,
    Group,
    LegendColumn,
    LegendLayout,
    LineMarker,
    LineType,
    LineWidth,
    LiveSpan,
    MarkerSeverity,
    Note,
    NotePreset,
    Palette,
    PopulatedTemplateVariable,
    Position,
    QueryValue,
    RangeMarker,
    Request,
    Scale,
    Size,
    Style,
    TemplateVariableDefinition,
    TemplateVariablesPreset,
    TextAlign,
    TickEdge,
    Time,
    Timeseries,
    Widget,
    YAxis,
)
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


def get_timeseries() -> Widget:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.AVG, by=By(tags=["availability-zone"])),
        funcs=[Fill(func=FillFunc.LINEAR), Rollup(func=RollupFunc.AVG, period_s=60)],
    )

    # Exercises most of the properties of a Timeseries
    widget = Timeseries(
        title="EC2: average CPU utilization per az",
        requests=[
            Request(
                queries=[query],
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
        size=Size(height=4, width=6),
        pos=Position(x=0, y=0),
    )

    return widget


def get_query_values() -> List[Widget]:
    query_all_reqs = Query(
        metric=Metric(name="aws.elb.request_count"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.SUM),
        funcs=[Fill(func=FillFunc.LINEAR), Rollup(func=RollupFunc.SUM, period_s=60)],
        name="reqs_all",
    )
    query_4xx = Query(
        metric=Metric(name="aws.elb.httpcode_elb_4xx"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.SUM),
        funcs=[Fill(func=FillFunc.LINEAR), Rollup(func=RollupFunc.SUM, period_s=60)],
        name="reqs_4xx",
    )
    query_5xx = Query(
        metric=Metric(name="aws.elb.httpcode_elb_5xx"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.SUM),
        funcs=[Fill(func=FillFunc.LINEAR), Rollup(func=RollupFunc.SUM, period_s=60)],
        name="reqs_5xx",
    )

    widgets: List[Widget] = []
    x = 6

    for name, query in (("4xx", query_4xx), ("5xx", query_5xx)):
        # Exercises most of the properties of a QueryValue
        widget = QueryValue(
            title=f"ELB {name.upper()}",
            time=Time(live_span=LiveSpan.LAST_1W),
            custom_unit="%",
            precision=1,
            requests=[
                Request(
                    formulas=[Formula(text=f"100 * (reqs_{name} / reqs_all)")],
                    queries=[query_all_reqs, query],
                    conditional_formats=[
                        ConditionalFormat(
                            comparator=Comparator.LT,
                            value=1,
                            palette=ConditionalFormatPalette.WHITE_ON_GREEN,
                        ),
                        ConditionalFormat(
                            comparator=Comparator.LT,
                            value=5,
                            palette=ConditionalFormatPalette.WHITE_ON_YELLOW,
                        ),
                        ConditionalFormat(
                            comparator=Comparator.GTE,
                            value=5,
                            palette=ConditionalFormatPalette.WHITE_ON_RED,
                        ),
                    ],
                ),
            ],
            size=Size(height=2, width=3),
            pos=Position(x=x, y=0),
        )
        x += 3
        widgets.append(widget)

    return widgets


def get_notes() -> List[Widget]:
    # Exercises most of the properties of a Note
    note_timeseries = Note(
        preset=NotePreset.ANNOTATION,
        content=(
            "**Timeseries** is the most general purpose widget that applies "
            "to virtually any use case."
        ),
        font_size=14,
        background_color=BackgroundColor.YELLOW,
        text_align=TextAlign.LEFT,
        tick_edge=TickEdge.LEFT,
        pos=Position(x=6, y=2),
        size=Size(width=3, height=2),
    )

    note_query_value = Note(
        preset=NotePreset.ANNOTATION,
        content=(
            "**QueryValue** is a widget often used on roll up dashboards to "
            "show a summary of a metric over time."
        ),
        font_size=14,
        background_color=BackgroundColor.PURPLE,
        text_align=TextAlign.LEFT,
        tick_edge=TickEdge.TOP,
        pos=Position(x=9, y=2),
        size=Size(width=3, height=2),
    )

    return [note_timeseries, note_query_value]


def get_group() -> Widget:
    wid_ec2_cpu = get_timeseries()
    wids_5xx_perc = get_query_values()
    wids_notes = get_notes()
    widgets: List[Widget] = [wid_ec2_cpu] + wids_5xx_perc + wids_notes

    # Exercises most of the properties of a Group
    group = Group(
        title="Exercise all supported widgets",
        background_color=BackgroundColor.VIVID_ORANGE,
        widgets=widgets,
    )

    return group


def get_dashboard() -> Dashboard:
    group = get_group()

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog QA: exercise widgets",
        desc=(
            "This dashboard is used exclusively for the purposes of integration "
            "testing **libddog**, which is an open source Datadog automation "
            "tool created by Nearmap.\n\n"
            "It is used during automated test runs as well as for manual (visual) "
            "inspection that everything looks correct.\n\n"
            "Get libddog on [Github](https://github.com/nearmap/libddog)."
        ),
        widgets=[group],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
