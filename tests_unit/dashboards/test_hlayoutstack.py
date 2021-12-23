from libddog.dashboards import HLayout, Note, NotePreset
from libddog.dashboards.layouts import HLayoutStack, HLayoutWrapping


def test_hlayoutstack__one_layer() -> None:
    # two widgets in a single row
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")

    stack = HLayoutStack(layouts=[HLayout(width=3, height=1, widgets=[fst, snd])])
    wids = stack.get_widgets()

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


def test_hlayoutstack__three_layers() -> None:
    # first row (has padding)
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")
    # second row (no padding)
    thd = Note(content="this is a third note")
    frth = Note(content="this is a fourth note")
    fith = Note(content="this is a fifth note")
    # third row (has padding)
    sth = Note(content="this is a sixth note")

    stack = HLayoutStack(
        layouts=[
            HLayout(width=5, height=3, widgets=[fst, snd]),
            HLayout(width=4, height=2, widgets=[thd, frth, fith]),
            HLayout(width=9, height=5, widgets=[sth]),
        ]
    )
    wids = stack.get_widgets()

    assert len(wids) == 8

    # row 1
    assert wids[0] is fst
    assert wids[1] is snd
    pad1 = wids[2]

    # row 2
    assert wids[3] is thd
    assert wids[4] is frth
    assert wids[5] is fith

    # row 3
    assert wids[6] is sth
    pad3 = wids[7]

    # row 1 detailed
    assert fst.size.width == 5
    assert fst.size.height == 3
    assert fst.position.x == 0
    assert fst.position.y == 0

    assert snd.size.width == 5
    assert snd.size.height == 3
    assert snd.position.x == 5
    assert snd.position.y == 0

    assert isinstance(pad1, Note)
    assert pad1.preset is NotePreset.CAPTION
    assert pad1.content == ""
    assert pad1.size.width == 2
    assert pad1.size.height == 3
    assert pad1.position.x == 10
    assert pad1.position.y == 0

    # row 2 detailed
    assert thd.size.width == 4
    assert thd.size.height == 2
    assert thd.position.x == 0
    assert thd.position.y == 3

    assert frth.size.width == 4
    assert frth.size.height == 2
    assert frth.position.x == 4
    assert frth.position.y == 3

    assert fith.size.width == 4
    assert fith.size.height == 2
    assert fith.position.x == 8
    assert fith.position.y == 3

    # row 3 detailed
    assert sth.size.width == 9
    assert sth.size.height == 5
    assert sth.position.x == 0
    assert sth.position.y == 5

    assert isinstance(pad3, Note)
    assert pad3.preset is NotePreset.CAPTION
    assert pad3.content == ""
    assert pad3.size.width == 3
    assert pad3.size.height == 5
    assert pad3.position.x == 9
    assert pad3.position.y == 5


def test_hlayoutstack__mix_hlayout_hlayoutwrapping() -> None:
    # first row (has padding)
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")
    # rows 2 and 3 (have padding)
    thd = Note(content="this is a third note")
    frth = Note(content="this is a fourth note")
    fith = Note(content="this is a fifth note")
    # fourth row (has padding)
    sth = Note(content="this is a sixth note")

    stack = HLayoutStack(
        layouts=[
            HLayout(width=5, height=3, widgets=[fst, snd]),
            HLayoutWrapping(width=5, height=2, widgets=[thd, frth, fith]),
            HLayout(width=9, height=5, widgets=[sth]),
        ]
    )
    wids = stack.get_widgets()

    assert len(wids) == 10

    # row 1
    assert wids[0] is fst
    assert wids[1] is snd
    pad1 = wids[2]

    # rows 2 and 3
    assert wids[3] is thd
    assert wids[4] is frth
    pad2 = wids[5]
    assert wids[6] is fith
    pad3 = wids[7]

    # row 4
    assert wids[8] is sth
    pad4 = wids[9]

    # row 1 detailed
    assert fst.size.width == 5
    assert fst.size.height == 3
    assert fst.position.x == 0
    assert fst.position.y == 0

    assert snd.size.width == 5
    assert snd.size.height == 3
    assert snd.position.x == 5
    assert snd.position.y == 0

    assert isinstance(pad1, Note)
    assert pad1.preset is NotePreset.CAPTION
    assert pad1.content == ""
    assert pad1.size.width == 2
    assert pad1.size.height == 3
    assert pad1.position.x == 10
    assert pad1.position.y == 0

    # row 2 detailed
    assert thd.size.width == 5
    assert thd.size.height == 2
    assert thd.position.x == 0
    assert thd.position.y == 3

    assert frth.size.width == 5
    assert frth.size.height == 2
    assert frth.position.x == 5
    assert frth.position.y == 3

    assert isinstance(pad2, Note)
    assert pad2.preset is NotePreset.CAPTION
    assert pad2.content == ""
    assert pad2.size.width == 2
    assert pad2.size.height == 2
    assert pad2.position.x == 10
    assert pad2.position.y == 3

    # row 3 detailed
    assert fith.size.width == 5
    assert fith.size.height == 2
    assert fith.position.x == 0
    assert fith.position.y == 5

    assert isinstance(pad3, Note)
    assert pad3.preset is NotePreset.CAPTION
    assert pad3.content == ""
    assert pad3.size.width == 7
    assert pad3.size.height == 2
    assert pad3.position.x == 5
    assert pad3.position.y == 5

    # row 4 detailed
    assert sth.size.width == 9
    assert sth.size.height == 5
    assert sth.position.x == 0
    assert sth.position.y == 7

    assert isinstance(pad4, Note)
    assert pad4.preset is NotePreset.CAPTION
    assert pad4.content == ""
    assert pad4.size.width == 3
    assert pad4.size.height == 5
    assert pad4.position.x == 9
    assert pad4.position.y == 7
