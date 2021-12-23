from dashboards.shared import get_dashboard_desc_template, get_region_tmpl_var_presets

from libddog.dashboards import (
    BackgroundColor,
    Dashboard,
    Group,
    HLayout,
    HLayoutStack,
    HLayoutWrapping,
    Note,
    Widget,
)


def get_note(id: str) -> Widget:
    return Note(
        content=f"this is the {id} note",
        background_color=BackgroundColor.YELLOW,
    )


def get_note_wrap(id: str) -> Widget:
    return Note(
        content=f"this is the {id} note",
        background_color=BackgroundColor.GREEN,
    )


def get_group_hlayout() -> Widget:
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
        title="Exercise HLayout",
        background_color=BackgroundColor.VIVID_ORANGE,
        widgets=widgets,
    )

    return group


def get_group_hlayoutwrapping() -> Widget:
    layout_width5 = HLayoutWrapping(
        width=5,
        height=1,
        widgets=[
            get_note_wrap("first"),
            get_note_wrap("second"),
            get_note_wrap("third"),
            get_note_wrap("fourth"),
            get_note_wrap("fifth"),
        ],
    )
    layout_width4 = HLayoutWrapping(
        width=4,
        height=2,
        widgets=[
            get_note_wrap("first"),
            get_note_wrap("second"),
            get_note_wrap("third"),
            get_note_wrap("fourth"),
            get_note_wrap("fifth"),
        ],
    )

    layout = HLayoutStack(layouts=[layout_width5, layout_width4])
    widgets = layout.get_widgets()

    # Exercises most of the configurations we can achieve with HLayout
    group = Group(
        title="Exercise HLayoutWrapping",
        background_color=BackgroundColor.VIVID_PURPLE,
        widgets=widgets,
    )

    return group


def get_group_hlayout_and_wrapping() -> Widget:
    layout_width5 = HLayoutWrapping(
        width=5,
        height=1,
        widgets=[
            get_note_wrap("first"),
            get_note_wrap("second"),
            get_note_wrap("third"),
            get_note_wrap("fourth"),
            get_note_wrap("fifth"),
        ],
    )
    layout_line = HLayout(
        width=4, height=2, widgets=[get_note("first"), get_note("second")]
    )

    layout = HLayoutStack(layouts=[layout_width5, layout_line])
    widgets = layout.get_widgets()

    # Exercises most of the configurations we can achieve with HLayout
    group = Group(
        title="Mix HLayout and HLayoutWrapping",
        background_color=BackgroundColor.VIVID_PINK,
        widgets=widgets,
    )

    return group


def get_dashboard() -> Dashboard:
    group_hlayout = get_group_hlayout()
    group_hlayoutwrapping = get_group_hlayoutwrapping()
    group_hlayout_and_wrapping = get_group_hlayout_and_wrapping()

    tmpl_presets_region = get_region_tmpl_var_presets()
    dashboard = Dashboard(
        title="libddog QA: exercise layouts",
        desc=get_dashboard_desc_template(),
        widgets=[group_hlayout, group_hlayoutwrapping, group_hlayout_and_wrapping],
        tmpl_var_presets=tmpl_presets_region,
    )

    return dashboard
