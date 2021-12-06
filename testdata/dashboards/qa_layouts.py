from dashboards.shared import get_dashboard_desc_template, get_region_tmpl_var_presets

from libddog.dashboards import BackgroundColor, Dashboard, Group, Note, Widget
from libddog.dashboards.layouts import HLayout, HLayoutStack


def get_note(id: str) -> Widget:
    return Note(
        content=f"this is the {id} note",
        background_color=BackgroundColor.YELLOW,
    )


def get_group() -> Widget:
    # first row
    fst = get_note("first")
    snd = get_note("second")
    # second row
    # third row
    thd = get_note("third")
    frth = get_note("fourth")
    fith = get_note("fifth")
    # fourth row
    sth = get_note("sixth")
    # fifth row

    layout = HLayoutStack(
        layouts=[
            HLayout(width=2, height=3, widgets=[fst, snd]),
            HLayout(width=5, height=1, widgets=[]),
            HLayout(width=4, height=2, widgets=[thd, frth, fith]),
            HLayout(width=9, height=5, widgets=[sth]),
            HLayout(width=2, height=2, widgets=[]),
        ]
    )
    widgets = layout.get_widgets()

    # Exercises most of the configurations we can achieve with HLayout
    group = Group(
        title="Exercise HLayout and HLayoutStack",
        background_color=BackgroundColor.VIVID_ORANGE,
        widgets=widgets,
    )

    return group


def get_dashboard() -> Dashboard:
    group = get_group()

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog QA: exercise layouts",
        desc=get_dashboard_desc_template(),
        widgets=[group],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
