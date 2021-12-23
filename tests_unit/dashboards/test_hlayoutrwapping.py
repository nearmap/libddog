from libddog.dashboards import HLayoutWrapping, Note, NotePreset, Position, Size


def test_hlayoutwrapping__overrides_size_and_position() -> None:
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

    layout = HLayoutWrapping(width=3, height=1, widgets=[fst, snd])
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


def test_hlayoutwrapping__wraps_without_padding() -> None:
    # create four notes that wrap over two lines, but wide enough to fill the
    # page width on each line
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")
    thd = Note(content="this is also a note")
    fth = Note(content="this is - guess what - a note")

    layout = HLayoutWrapping(width=6, height=4, widgets=[fst, snd, thd, fth])
    wids = layout.get_widgets()

    # the four widgets are the ones we gave it
    assert len(wids) == 4
    assert fst is wids[0]
    assert snd is wids[1]
    assert thd is wids[2]
    assert fth is wids[3]

    assert fst.size.width == 6
    assert fst.size.height == 4
    assert fst.position.x == 0
    assert fst.position.y == 0

    assert snd.size.width == 6
    assert snd.size.height == 4
    assert snd.position.x == 6
    assert snd.position.y == 0

    assert thd.size.width == 6
    assert thd.size.height == 4
    assert thd.position.x == 0
    assert thd.position.y == 4

    assert fth.size.width == 6
    assert fth.size.height == 4
    assert fth.position.x == 6
    assert fth.position.y == 4


def test_hlayoutwrapping__wraps_with_padding() -> None:
    # create two notes that wrap over two lines but do not fill the page width
    # on those lines
    fst = Note(content="this is a note")
    snd = Note(content="this is another note")

    layout = HLayoutWrapping(width=9, height=3, widgets=[fst, snd])
    wids = layout.get_widgets()

    # there are two padding widgets
    assert len(wids) == 4

    # the widgets we gave it are interleaved with padding widgets
    assert fst is wids[0]
    pad1 = wids[1]
    assert snd is wids[2]
    pad2 = wids[3]

    assert fst.size.width == 9
    assert fst.size.height == 3
    assert fst.position.x == 0
    assert fst.position.y == 0

    assert pad1.size.width == 3
    assert pad1.size.height == 3
    assert pad1.position.x == 9
    assert pad1.position.y == 0

    assert snd.size.width == 9
    assert snd.size.height == 3
    assert snd.position.x == 0
    assert snd.position.y == 3

    assert pad2.size.width == 3
    assert pad2.size.height == 3
    assert pad2.position.x == 9
    assert pad2.position.y == 3

    # the padding widgets are Notes that look transparent
    assert isinstance(pad1, Note)
    assert pad1.preset is NotePreset.CAPTION
    assert pad1.content == ""

    assert isinstance(pad2, Note)
    assert pad2.preset is NotePreset.CAPTION
    assert pad2.content == ""


# Corner cases


def test_hlayoutwrapping__empty() -> None:
    # create a layout without any widgets
    layout = HLayoutWrapping(width=4, height=2, widgets=[])
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
