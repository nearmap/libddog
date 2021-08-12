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
    Add,
    AggFunc,
    Aggregation,
    By,
    Comma,
    Div,
    Fill,
    FillFunc,
    Filter,
    Int,
    Metric,
    Mul,
    Query,
    Rollup,
    RollupFunc,
    Sub,
    TmplVar,
    abs,
    log2,
    log10,
)


def get_formulas_group() -> Widget:
    query = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.AVG),
        name="cpu",
    )

    widget = Timeseries(
        title="All arith operators",
        requests=[
            Request(
                formulas=[
                    Formula(text="((abs(cpu) * 2) - cpu) + log2(cpu) / log10(cpu)")
                ],
                queries=[query],
            ),
        ],
        size=Size(height=2, width=3),
        position=Position(x=0, y=0),
    )

    group = Group(
        title="Exercise formulas",
        widgets=[widget],
    )

    return group


def get_dashboard() -> Dashboard:
    formulas = get_formulas_group()

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog QA: exercise metrics and query strings",
        desc=get_dashboard_desc_template(),
        widgets=[formulas],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
