import pytest

from libddog.dashboards import HLayout, Note, NotePreset, Position, Size
from libddog.dashboards.exceptions import HLayoutError


def test_hlayout__overrides_size_and_position() -> None:
    # create two notes with very random sizes and positions
    fst = Note(
        content="this is a note",
        size=Size(width=5, height=7),
        position=Position(x=3, y=9),
    )
    snd = Note(
        content="this is another note",
        size=Size(width=8, height=1),
        position=Position(x=2, y=0),
    )

    layout = HLayout(width=3, height=1, widgets=[fst, snd])
    wids = layout.get_widgets()

    # the two widgets are the ones we gave it
    assert fst is wids[0]
    assert snd is wids[1]

    # the sizes and positions have been overridden by the layout
    assert fst.size.width == 3
    assert fst.size.height == 1
    assert fst.position.x == 0
    assert fst.position.y == 0

    assert snd.size.width == 3
    assert snd.size.height == 1
    assert snd.position.x == 3
    assert snd.position.y == 0


def test_hlayout__adds_padding() -> None:
    # create two notes that are not wide enough to fill the page width
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")

    layout = HLayout(width=3, height=1, widgets=[fst, snd])
    wids = layout.get_widgets()

    # the first two widgets are the ones we gave it
    assert fst is wids[0]
    assert snd is wids[1]

    assert fst.size.width == 3
    assert fst.size.height == 1
    assert fst.position.x == 0
    assert fst.position.y == 0

    assert snd.size.width == 3
    assert snd.size.height == 1
    assert snd.position.x == 3
    assert snd.position.y == 0

    # there is a third padding widget
    assert len(wids) == 3
    pad = wids[2]

    # it's a Note that looks transparent
    assert isinstance(pad, Note)
    assert pad.preset is NotePreset.CAPTION
    assert pad.content == ""

    # it's on the same line and extends until the end of the page
    assert pad.size.width == 6
    assert pad.size.height == 1
    assert pad.position.x == 6
    assert pad.position.y == 0


def test_hlayout__no_padding() -> None:
    # create two notes that ARE wide enough to fill the page width
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")

    layout = HLayout(width=6, height=2, widgets=[fst, snd])
    wids = layout.get_widgets()

    # the only two widgets are the ones we gave it
    assert len(wids) == 2
    assert fst is wids[0]
    assert snd is wids[1]

    assert fst.size.width == 6
    assert fst.size.height == 2
    assert fst.position.x == 0
    assert fst.position.y == 0

    assert snd.size.width == 6
    assert snd.size.height == 2
    assert snd.position.x == 6
    assert snd.position.y == 0


# Corner cases


def test_hlayout__empty() -> None:
    # create a layout without any widgets
    layout = HLayout(width=4, height=2, widgets=[])
    wids = layout.get_widgets()

    # we get a single padding widget that fills the page width
    assert len(wids) == 1
    pad = wids[0]

    # it's a Note that looks transparent
    assert isinstance(pad, Note)
    assert pad.preset is NotePreset.CAPTION
    assert pad.content == ""

    # it extends until the end of the page
    assert pad.size.width == 12
    assert pad.size.height == 2
    assert pad.position.x == 0
    assert pad.position.y == 0


def test_hlayout__overflows_page_width() -> None:
    # create two notes that are wider than the page width
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")

    layout = HLayout(width=9, height=2, widgets=[fst, snd])

    with pytest.raises(HLayoutError) as ctx:
        layout.get_widgets()

    assert ctx.value.args[0] == "Overflowed page width (12) by 6 units"
