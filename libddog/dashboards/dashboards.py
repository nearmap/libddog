from typing import List, Optional, Sequence

from libddog.common.bases import Renderable
from libddog.common.types import JsonDict
from libddog.dashboards.components import (
    TemplateVariableDefinition,
    TemplateVariablesPreset,
)
from libddog.dashboards.widgets import Widget


class Dashboard(Renderable):
    def __init__(
        self,
        *,
        id: Optional[str] = None,
        title: str,
        desc: str = "",
        widgets: Optional[Sequence[Widget]] = None,
        tmpl_var_defs: Optional[List[TemplateVariableDefinition]] = None,
        tmpl_var_presets: Optional[List[TemplateVariablesPreset]] = None,
    ) -> None:
        self.id = id
        self.title = title
        self.desc = desc
        self.widgets = widgets or []
        self.tmpl_var_defs = tmpl_var_defs or []
        self.tmpl_var_presets = tmpl_var_presets or []

        # infer tmpl_var definitions from the presets
        for preset in self.tmpl_var_presets:
            for populated_var in preset.populated_vars:
                if populated_var.tmpl_var not in self.tmpl_var_defs:
                    self.tmpl_var_defs.append(populated_var.tmpl_var)

    def as_dict(self) -> JsonDict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.desc,
            "widgets": [wid.as_dict() for wid in self.widgets],
            "template_variables": [tmp.as_dict() for tmp in self.tmpl_var_defs],
            "template_variable_presets": [
                pres.as_dict() for pres in self.tmpl_var_presets
            ],
            "layout_type": "ordered",
            "is_read_only": False,
            "notify_list": [],
            "reflow_type": "fixed",
        }
