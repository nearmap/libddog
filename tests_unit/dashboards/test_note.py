from libddog.dashboards import (
    BackgroundColor,
    Note,
    NotePreset,
    Position,
    Size,
    TextAlign,
    TickEdge,
    VerticalAlign,
)


def test_note__minimal() -> None:
    note = Note(
        content="this is a note",
    )

    assert note.as_dict() == {
        "definition": {
            "background_color": "white",
            "content": "this is a note",
            "font_size": "14",
            "has_padding": True,
            "show_tick": False,
            "text_align": "left",
            "tick_edge": "top",
            "type": "note",
            "vertical_align": "top",
        },
        "layout": {"height": 2, "width": 2, "x": 0, "y": 0},
    }


def test_note__exhaustive() -> None:
    # override all the values such that they differ from the preset
    note = Note(
        preset=NotePreset.ANNOTATION,
        content="this is a note",
        background_color=BackgroundColor.VIVID_YELLOW,
        font_size=17,
        text_align=TextAlign.RIGHT,
        vertical_align=VerticalAlign.BOTTOM,
        show_tick=False,
        tick_edge=TickEdge.BOTTOM,
        has_padding=False,
        size=Size(width=4, height=5),
        position=Position(x=6, y=7),
    )

    assert note.as_dict() == {
        "definition": {
            "background_color": "vivid_yellow",
            "content": "this is a note",
            "font_size": "17",
            "has_padding": False,
            "show_tick": False,
            "text_align": "right",
            "tick_edge": "bottom",
            "type": "note",
            "vertical_align": "bottom",
        },
        "layout": {"height": 5, "width": 4, "x": 6, "y": 7},
    }


def test_note__no_preset_equals_default_preset() -> None:
    note_no_preset = Note(
        content="this is a note",
    )

    note_default = Note(
        preset=NotePreset.DEFAULT,
        content="this is a note",
    )

    assert note_no_preset.as_dict() == note_default.as_dict()


def test_note_caption__minimal() -> None:
    note = Note(
        preset=NotePreset.CAPTION,
        content="this is a note",
    )

    assert note.as_dict() == {
        "definition": {
            "background_color": "transparent",
            "content": "this is a note",
            "font_size": "12",
            "has_padding": False,
            "show_tick": False,
            "text_align": "left",
            "tick_edge": "left",
            "type": "note",
            "vertical_align": "top",
        },
        "layout": {"height": 2, "width": 2, "x": 0, "y": 0},
    }


def test_note_header__minimal() -> None:
    note = Note(
        preset=NotePreset.HEADER,
        content="this is a note",
    )

    assert note.as_dict() == {
        "definition": {
            "background_color": "white",
            "content": "this is a note",
            "font_size": "36",
            "has_padding": True,
            "show_tick": False,
            "text_align": "center",
            "tick_edge": "left",
            "type": "note",
            "vertical_align": "center",
        },
        "layout": {"height": 2, "width": 2, "x": 0, "y": 0},
    }


def test_note_annotation__minimal() -> None:
    note = Note(
        preset=NotePreset.ANNOTATION,
        content="this is a note",
    )

    assert note.as_dict() == {
        "definition": {
            "background_color": "yellow",
            "content": "this is a note",
            "font_size": "14",
            "has_padding": True,
            "show_tick": True,
            "text_align": "left",
            "tick_edge": "left",
            "type": "note",
            "vertical_align": "center",
        },
        "layout": {"height": 2, "width": 2, "x": 0, "y": 0},
    }
