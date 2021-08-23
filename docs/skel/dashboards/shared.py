from typing import List

from libddog.dashboards import (
    PopulatedTemplateVariable,
    TemplateVariableDefinition,
    TemplateVariablesPreset,
)


def get_region_tmpl_var_presets() -> List[TemplateVariablesPreset]:
    presets = []
    popular_regions = ["ap-southeast-2", "us-east-1", "us-west-1", "eu-west-1"]

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
