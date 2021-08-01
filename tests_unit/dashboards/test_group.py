from libddog.dashboards import BackgroundColor, Group, LayoutType, Note


def test_group_minimal() -> None:
    group = Group(
        title="EC2 instances",
        layout_type=LayoutType.ORDERED,
    )

    assert group.as_dict() == {
        "definition": {
            "layout_type": "ordered",
            "title": "EC2 instances",
            "type": "group",
            "widgets": [],
        },
    }


def test_group_exhaustive() -> None:
    note1 = Note(
        content="first note",
    )
    note2 = Note(
        content="second note",
    )

    group = Group(
        title="EC2 instances",
        layout_type=LayoutType.ORDERED,
        background_color=BackgroundColor.PURPLE,
        widgets=[note1, note2],
    )

    assert group.as_dict() == {
        "definition": {
            "background_color": "purple",
            "layout_type": "ordered",
            "title": "EC2 instances",
            "type": "group",
            "widgets": [note1.as_dict(), note2.as_dict()],
        },
    }
