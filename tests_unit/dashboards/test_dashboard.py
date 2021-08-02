from libddog.dashboards import Dashboard


def test_dashboard__minimal() -> None:
    dash = Dashboard(
        title="EC2 instances",
    )

    assert dash.as_dict() == {
        "description": "",
        "id": None,
        "is_read_only": False,
        "layout_type": "ordered",
        "notify_list": [],
        "reflow_type": "fixed",
        "template_variable_presets": [],
        "template_variables": [],
        "title": "EC2 instances",
        "widgets": [],
    }


def test_dashboard__exhaustive_shallow() -> None:
    dash = Dashboard(
        id="abc-123",
        title="EC2 instances",
        desc="Displays all our EC2 instances",
        widgets=[],
        tmpl_var_defs=[],
        tmpl_var_presets=[],
    )

    assert dash.as_dict() == {
        "description": "Displays all our EC2 instances",
        "id": "abc-123",
        "is_read_only": False,
        "layout_type": "ordered",
        "notify_list": [],
        "reflow_type": "fixed",
        "template_variable_presets": [],
        "template_variables": [],
        "title": "EC2 instances",
        "widgets": [],
    }
