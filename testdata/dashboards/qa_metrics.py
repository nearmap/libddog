from dashboards.shared import get_dashboard_desc_template, get_region_tmpl_var_presets

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
    Comma,
    Float,
    Int,
    Query,
    abs,
    anomalies,
    autosmooth,
    clamp_max,
    clamp_min,
    count_nonzero,
    count_not_null,
    cumsum,
    cutoff_max,
    cutoff_min,
    day_before,
    default_zero,
    derivative,
    diff,
    dt,
    ewma_3,
    ewma_5,
    ewma_10,
    ewma_20,
    exclude_null,
    forecast,
    hour_before,
    integral,
    log2,
    log10,
    median_3,
    median_5,
    median_7,
    median_9,
    monotonic_diff,
    month_before,
    moving_rollup,
    outliers,
    per_hour,
    per_minute,
    per_second,
    piecewise_constant,
    robust_trend,
    timeshift,
    top,
    trend_line,
    week_before,
)

QUERY_CASES = [
    ("minimal query", Query("aws.ec2.cpuutilization").agg("avg")),
    (
        "exhaustive query",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "no aggregation",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "aggregation without as",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .agg("avg")
            .by("availability-zone")
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "aggregation without by",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .agg("avg")
            .as_rate()
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "aggregation without by/as",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .agg("avg")
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "no filter",
        (
            Query("aws.ec2.cpuutilization")
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "inclusive filter",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region", **{"availability-zone": "*a"})
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "negating tag filter",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .filter_ne(**{"availability-zone": "*a"})
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "negating tmpl var filter",
        (
            Query("aws.ec2.cpuutilization")
            .filter_ne("$region")
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .rollup("max", 110)
            .fill("last", 112)
        ),
    ),
    (
        "no rollup",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .fill("last", 112)
        ),
    ),
    (
        "no fill",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .rollup("max", 110)
        ),
    ),
    (
        "fill before rollup",
        (
            Query("aws.ec2.cpuutilization")
            .filter("$region")
            .agg("avg")
            .by("availability-zone")
            .as_rate()
            .fill("last", 112)
            .rollup("max", 110)
        ),
    ),
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
    query_cpu = Query("aws.ec2.cpuutilization", name="cpu").filter("$region").agg("avg")
    query_reqs = (
        Query("aws.elb.request_count", name="reqs").filter("$region").agg("avg")
    )

    cpu = query_cpu.identifier()
    reqs = query_reqs.identifier()

    cases = [
        (
            "All arithmetic operators",
            (
                ((abs(cpu) * Int(2)) - reqs)
                + (Float(3.14) * log2(cpu) / timeshift(reqs, -3600))
            ),
        ),
        (
            "Comma as binary operator",
            Comma(cpu, reqs),
        ),
        (
            "Nested function application",
            log2(abs(cpu)),
        ),
        (
            "Function applied to formula",
            log2(abs(cpu) / log10(reqs)),
        ),
    ]

    widgets = []
    x, y = 0, 0

    for title, formula in cases:
        widget = Timeseries(
            title=title,
            requests=[
                Request(
                    formulas=[Formula(formula=formula)],
                    queries=[query_cpu, query_reqs],
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
    query_reqs = (
        Query("aws.elb.request_count", name="reqs").filter("$region").agg("avg")
    )

    reqs = query_reqs.identifier()

    cases = [
        # arithmetic
        ("abs", abs(reqs)),
        ("log2", log2(reqs)),
        ("log10", log10(reqs)),
        ("cumsum", cumsum(reqs)),
        ("integral", integral(reqs)),
        # interpolation
        ("default_zero", default_zero(reqs)),
        # timeshift
        ("hour_before", hour_before(reqs)),
        ("day_before", day_before(reqs)),
        ("week_before", week_before(reqs)),
        ("month_before", month_before(reqs)),
        ("timeshift -1h", timeshift(reqs, -3600)),
        # rate
        ("per_second", per_second(reqs)),
        ("per_minute", per_minute(reqs)),
        ("per_hour", per_hour(reqs)),
        ("dt", dt(reqs)),
        ("diff", diff(reqs)),
        ("monotonic_diff", monotonic_diff(reqs)),
        ("derivative", derivative(reqs)),
        # smoothing
        ("autosmooth", autosmooth(reqs)),
        ("ewma_3", ewma_3(reqs)),
        ("ewma_5", ewma_5(reqs)),
        ("ewma_10", ewma_10(reqs)),
        ("ewma_20", ewma_20(reqs)),
        ("median_3", median_3(reqs)),
        ("median_5", median_5(reqs)),
        ("median_7", median_7(reqs)),
        ("median_9", median_9(reqs)),
        # rollup
        ("moving_rollup", moving_rollup(reqs, 180, "sum")),
        # top
        ("top", top(reqs, 5, "sum", "asc")),
        # count
        ("count_nonzero", count_nonzero(reqs)),
        ("count_not_null", count_not_null(reqs)),
        # regression
        ("robust_trend", robust_trend(reqs)),
        ("trend_line", trend_line(reqs)),
        ("piecewise_constant", piecewise_constant(reqs)),
        # algorithms
        ("outliers", outliers(reqs, "DBSCAN", 2.0)),
        ("anomalies", anomalies(reqs, "agile", 2)),
        ("forecast", forecast(reqs, "linear", 2)),
        # exclusion
        ("exclude_null", exclude_null(reqs, "availability-zone")),
        ("cutoff_max 2", cutoff_max(reqs, 2)),
        ("cutoff_min 1", cutoff_min(reqs, 1)),
        ("clamp_max 2", clamp_max(reqs, 2)),
        ("clamp_min 1", clamp_min(reqs, 1)),
    ]

    widgets = []
    x, y = 0, 0

    for title, formula in cases:
        widget = Timeseries(
            title=title,
            requests=[
                Request(
                    formulas=[
                        Formula(formula=reqs, alias="source"),
                        Formula(formula=formula, alias=title),
                    ],
                    queries=[query_reqs],
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
