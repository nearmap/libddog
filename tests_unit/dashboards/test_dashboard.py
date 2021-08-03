from libddog.dashboards import (
    Dashboard,
    PopulatedTemplateVariable,
    TemplateVariableDefinition,
    TemplateVariablesPreset,
)


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


# template var cases


def test_dashboard__templ_vars_without_preset() -> None:
    def_az = TemplateVariableDefinition(
        name="az",
        tag="availability_zone",
        default_value="*",
    )
    def_role = TemplateVariableDefinition(
        name="role",
        tag="workload_role",
        default_value="*",
    )

    dash = Dashboard(
        title="EC2 instances",
        widgets=[],
        tmpl_var_defs=[def_az, def_role],
        tmpl_var_presets=[],
    )

    assert dash.as_dict() == {
        "description": "",
        "id": None,
        "is_read_only": False,
        "layout_type": "ordered",
        "notify_list": [],
        "reflow_type": "fixed",
        "template_variable_presets": [],
        "template_variables": [
            {"default": "*", "name": "az", "prefix": "availability_zone"},
            {"default": "*", "name": "role", "prefix": "workload_role"},
        ],
        "title": "EC2 instances",
        "widgets": [],
    }


def test_dashboard__infer_templ_vars_from_templ_preset() -> None:
    def_az = TemplateVariableDefinition(
        name="az",
        tag="availability_zone",
        default_value="*",
    )
    def_role = TemplateVariableDefinition(
        name="role",
        tag="workload_role",
        default_value="*",
    )

    pop_az = PopulatedTemplateVariable(
        tmpl_var=def_az,
        value="us-east-1a",
    )
    pop_role = PopulatedTemplateVariable(
        tmpl_var=def_role,
        value="cache",
    )

    preset = TemplateVariablesPreset(
        name="favorite-az-and-role",
        populated_vars=[pop_az, pop_role],
    )

    dash = Dashboard(
        title="EC2 instances",
        widgets=[],
        tmpl_var_defs=[],
        tmpl_var_presets=[preset],
    )

    assert dash.as_dict() == {
        "description": "",
        "id": None,
        "is_read_only": False,
        "layout_type": "ordered",
        "notify_list": [],
        "reflow_type": "fixed",
        "template_variable_presets": [
            {
                "name": "favorite-az-and-role",
                "template_variables": [
                    {"name": "az", "value": "us-east-1a"},
                    {"name": "role", "value": "cache"},
                ],
            }
        ],
        "template_variables": [
            {"default": "*", "name": "az", "prefix": "availability_zone"},
            {"default": "*", "name": "role", "prefix": "workload_role"},
        ],
        "title": "EC2 instances",
        "widgets": [],
    }
