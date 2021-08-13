from typing import List

from libddog.dashboards import (
    PopulatedTemplateVariable,
    TemplateVariableDefinition,
    TemplateVariablesPreset,
)


def get_dashboard_desc_template() -> str:
    desc = (
        "This dashboard is used exclusively for the purposes of integration "
        "testing [libddog](https://github.com/nearmap/libddog), which is an "
        "open source Datadog automation tool created by Nearmap.\n\n"
        "It is used during automated test runs as well as for manual (visual) "
        "inspection that everything looks correct.\n\n"
        "Last updated during test run on: *%(test_run_time)s*"
    )
    return desc


def get_region_tmpl_var_presets() -> List[TemplateVariablesPreset]:
    presets = []
    popular_regions = ["ap-southeast-2", "us-east-1", "us-west-1"]

    defn = TemplateVariableDefinition(
        name="region",
        tag="region",
        default_value="us-east-1",
    )

    for region in popular_regions:
        preset = TemplateVariablesPreset(
            name=region,
            populated_vars=[
                PopulatedTemplateVariable(
                    tmpl_var=defn,
                    value=region,
                )
            ],
        )
        presets.append(preset)

    return presets
