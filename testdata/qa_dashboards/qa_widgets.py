from typing import List

from qa_dashboards.shared import (
    get_dashboard_desc_template,
    get_region_tmpl_var_presets,
)

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
    Position,
    QueryValue,
    RangeMarker,
    Request,
    Scale,
    Size,
    Style,
    TextAlign,
    TickEdge,
    Time,
    Timeseries,
    Widget,
    YAxis,
)
from libddog.metrics import Int, Query


def get_timeseries() -> Widget:
    query = (
        Query("aws.ec2.cpuutilization")
        .filter("$region")
        .agg("avg")
        .by("availability-zone")
        .fill("linear")
        .rollup("avg", 60)
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
        position=Position(x=0, y=0),
    )

    return widget


def get_query_values() -> List[Widget]:
    query_all_reqs = (
        Query("aws.elb.request_count", name="reqs_all")
        .filter("$region")
        .agg("sum")
        .fill("linear")
        .rollup("sum", 60)
    )
    query_4xx = (
        Query("aws.elb.httpcode_elb_4xx", name="reqs_4xx")
        .filter("$region")
        .agg("sum")
        .fill("linear")
        .rollup("sum", 60)
    )
    query_5xx = (
        Query("aws.elb.httpcode_elb_5xx", name="reqs_5xx")
        .filter("$region")
        .agg("sum")
        .fill("linear")
        .rollup("sum", 60)
    )

    reqs_all = query_all_reqs.identifier()

    widgets: List[Widget] = []
    x = 6

    for name, query in (("4xx", query_4xx), ("5xx", query_5xx)):
        reqs_this = query.identifier()

        # Exercises most of the properties of a QueryValue
        widget = QueryValue(
            title=f"ELB {name.upper()}",
            time=Time(live_span=LiveSpan.LAST_1W),
            custom_unit="%",
            precision=1,
            requests=[
                Request(
                    formulas=[Formula(formula=Int(100) * (reqs_this / reqs_all))],
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
            position=Position(x=x, y=0),
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
        position=Position(x=6, y=2),
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
        position=Position(x=9, y=2),
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
        desc=get_dashboard_desc_template(),
        widgets=[group],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
