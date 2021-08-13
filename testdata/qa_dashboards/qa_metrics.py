from qa_dashboards.shared import (
    get_dashboard_desc_template,
    get_region_tmpl_var_presets,
)

from libddog.dashboards import (
    Dashboard,
    Formula,
    Group,
    Note,
    NotePreset,
    Position,
    Request,
    Size,
    Timeseries,
    Widget,
)
from libddog.metrics import (
    AggFunc,
    Aggregation,
    As,
    By,
    Fill,
    FillFunc,
    Filter,
    FilterOperator,
    Metric,
    Query,
    Rollup,
    RollupFunc,
    Tag,
    TmplVar,
)

QUERY_CASES = [
    (
        "minimal query",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            agg=Aggregation(func=AggFunc.AVG),
        ),
    ),
    (
        "exhaustive query",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            agg=Aggregation(
                func=AggFunc.AVG, by=By(tags=["availability-zone"]), as_=As.RATE
            ),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "no aggregation",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "aggregation without as",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            agg=Aggregation(func=AggFunc.AVG, by=By(tags=["availability-zone"])),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "aggregation without by",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            agg=Aggregation(func=AggFunc.AVG, as_=As.RATE),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "aggregation without by/as",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            agg=Aggregation(func=AggFunc.AVG),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "no filter",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            agg=Aggregation(
                func=AggFunc.AVG, by=By(tags=["availability-zone"]), as_=As.RATE
            ),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "inclusive filter",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(
                conds=[
                    TmplVar(tvar="region"),
                    Tag(
                        tag="availability-zone",
                        value="*a",
                    ),
                ]
            ),
            agg=Aggregation(
                func=AggFunc.AVG, by=By(tags=["availability-zone"]), as_=As.RATE
            ),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "negating filter",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(
                conds=[
                    TmplVar(tvar="region"),
                    Tag(
                        tag="availability-zone",
                        value="*a",
                        operator=FilterOperator.NOT_EQUAL,
                    ),
                ]
            ),
            agg=Aggregation(
                func=AggFunc.AVG, by=By(tags=["availability-zone"]), as_=As.RATE
            ),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "no rollup",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            agg=Aggregation(
                func=AggFunc.AVG, by=By(tags=["availability-zone"]), as_=As.RATE
            ),
            funcs=[
                Fill(func=FillFunc.LAST, limit_s=112),
            ],
        ),
    ),
    (
        "no fill",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            agg=Aggregation(
                func=AggFunc.AVG, by=By(tags=["availability-zone"]), as_=As.RATE
            ),
            funcs=[
                Rollup(func=RollupFunc.MAX, period_s=110),
            ],
        ),
    ),
    (
        "fill before rollup",
        Query(
            metric=Metric(name="aws.ec2.cpuutilization"),
            filter=Filter(conds=[TmplVar(tvar="region")]),
            agg=Aggregation(
                func=AggFunc.AVG, by=By(tags=["availability-zone"]), as_=As.RATE
            ),
            funcs=[
                Fill(func=FillFunc.LAST, limit_s=112),
                Rollup(func=RollupFunc.MAX, period_s=110),
            ],
        ),
    ),
]

FORMULA_CASES = [
    (
        "All arithmetic operators",
        "((abs(cpu) * 2) - reqs) + (log2(cpu) / timeshift(reqs, -3600))",
    ),
    (
        "Comma as binary operator",
        "cpu, reqs",
    ),
    (
        "Nested function application",
        "log2(abs(cpu))",
    ),
    (
        "Function applied to formula",
        "log2(abs(cpu) / log10(reqs))",
    ),
]

FUNCTION_CASES = [
    # arithmetic
    ("abs", "abs(reqs)"),
    ("log2", "log2(reqs)"),
    ("log10", "log10(reqs)"),
    ("cumsum", "cumsum(reqs)"),
    ("integral", "integral(reqs)"),
    # interpolation
    ("default_zero", "default_zero(reqs)"),
    # timeshift
    ("hour_before", "hour_before(reqs)"),
    ("day_before", "day_before(reqs)"),
    ("week_before", "week_before(reqs)"),
    ("month_before", "month_before(reqs)"),
    ("timeshift -1h", "timeshift(reqs, -3600)"),
    # rate
    ("per_second", "per_second(reqs)"),
    ("per_minute", "per_minute(reqs)"),
    ("per_hour", "per_hour(reqs)"),
    ("dt", "dt(reqs)"),
    ("diff", "diff(reqs)"),
    ("monotonic_diff", "monotonic_diff(reqs)"),
    ("derivative", "derivative(reqs)"),
    # smoothing
    ("autosmooth", "autosmooth(reqs)"),
    ("ewma_3", "ewma_3(reqs)"),
    ("ewma_5", "ewma_5(reqs)"),
    ("ewma_10", "ewma_10(reqs)"),
    ("ewma_20", "ewma_20(reqs)"),
    ("median_3", "median_3(reqs)"),
    ("median_5", "median_5(reqs)"),
    ("median_7", "median_7(reqs)"),
    ("median_9", "median_9(reqs)"),
    # rollup
    ("moving_rollup", "moving_rollup(reqs, 180, 'sum')"),
    # top
    ("top", "top(reqs, 5, 'sum', 'asc')"),
    # count
    ("count_nonzero", "count_nonzero(reqs)"),
    ("count_not_null", "count_not_null(reqs)"),
    # regression
    ("robust_trend", "robust_trend(reqs)"),
    ("trend_line", "trend_line(reqs)"),
    ("piecewise_constant", "piecewise_constant(reqs)"),
    # algorithms
    ("outliers", "outliers(reqs, 'DBSCAN', 2.0)"),
    ("anomalies", "anomalies(reqs, 'agile', 2)"),
    ("forecast", "forecast(reqs, 'linear', 2)"),
    # exclusion
    ("exclude_null", "exclude_null(reqs, 'availability-zone')"),
    ("cutoff_max 2", "cutoff_max(reqs, 2)"),
    ("cutoff_min 1", "cutoff_min(reqs, 1)"),
    ("clamp_max 2", "clamp_max(reqs, 2)"),
    ("clamp_min 1", "clamp_min(reqs, 1)"),
]


def get_desc_group() -> Widget:
    note = Note(
        preset=NotePreset.ANNOTATION,
        content=(
            "We use this dashboard to demonstrate as many possible variations "
            "of queries, formulas and functions as possible.\n\n"
            "The way we do this is a bit oversimplified because we are using "
            "the same timeseries widget for every use case, with the same "
            "one or two metrics used in every graph. This is a good fit for "
            "some functions, but less good for others.\n\n"
            "As a result, we are not really concerned with the lines in the "
            "graps showing the right number, **just that the graph works and "
            "that the query string was accepted as valid by the Datadog API**. "
            "When we open the widget settings for each widget **we want the "
            "UI to correctly reflect the query in our model**, without "
            "components of it being discarded by Datadog as invalid.\n\n"
            "It's not strictly necessary that the graph have data in it, but "
            "it does make it much easier to QA, because we already know that "
            "the query was accepted and executed by the Datadog backend."
        ),
        show_tick=False,
        size=Size(width=12, height=3),
    )

    group = Group(
        title="How to use this dashboard to QA metrics queries",
        widgets=[note],
    )

    return group


def get_queries_group() -> Widget:
    x, y = 0, 0
    widgets = []

    for title, query in QUERY_CASES:
        widget = Timeseries(
            title=title,
            requests=[
                Request(
                    queries=[query],
                ),
            ],
            position=Position(x=x, y=y),
            size=Size(width=3, height=2),
        )
        widgets.append(widget)
        x += 3

        if x == 12:
            x = 0
            y += 2

    group = Group(
        title="Combinations and permutations of the components of a query",
        widgets=widgets,
    )

    return group


def get_formulas_group() -> Widget:
    cpu = Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.AVG),
        name="cpu",
    )
    reqs = Query(
        metric=Metric(name="aws.elb.request_count"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.AVG),
        name="reqs",
    )

    widgets = []
    x, y = 0, 0

    for title, text in FORMULA_CASES:
        widget = Timeseries(
            title=title,
            requests=[
                Request(
                    formulas=[Formula(text=text)],
                    queries=[cpu, reqs],
                ),
            ],
            position=Position(x=x, y=y),
            size=Size(width=3, height=2),
        )
        widgets.append(widget)
        x += 3

        if x == 12:
            x = 0
            y += 2

    group = Group(
        title="Exercise formulas",
        widgets=widgets,
    )

    return group


def get_functions_group() -> Widget:
    reqs = Query(
        metric=Metric(name="aws.elb.request_count"),
        filter=Filter(conds=[TmplVar(tvar="region")]),
        agg=Aggregation(func=AggFunc.AVG),
        name="reqs",
    )

    widgets = []
    x, y = 0, 0

    for title, text in FUNCTION_CASES:
        widget = Timeseries(
            title=title,
            requests=[
                Request(
                    formulas=[
                        Formula(text="reqs", alias="source"),
                        Formula(text=text, alias=title),
                    ],
                    queries=[reqs],
                ),
            ],
            position=Position(x=x, y=y),
            size=Size(width=3, height=2),
        )
        widgets.append(widget)
        x += 3

        if x == 12:
            x = 0
            y += 2

    group = Group(
        title="Exercise functions",
        widgets=widgets,
    )

    return group


def get_dashboard() -> Dashboard:
    desc = get_desc_group()
    queries = get_queries_group()
    formulas = get_formulas_group()
    functions = get_functions_group()

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog QA: exercise metrics queries",
        desc=get_dashboard_desc_template(),
        widgets=[desc, queries, formulas, functions],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
