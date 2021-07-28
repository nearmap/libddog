from typing import Any, Dict, Iterator

from libddog.dashboards.components import TemplateVariableDefinition


def get_template_vars(doc: Dict[Any, Any]) -> Iterator[TemplateVariableDefinition]:
    tmpl_vars = doc.get("template_variables") or []

    for var in tmpl_vars:
        default_value = var.get("default")
        name = var["name"]
        tag = var["prefix"]

        yield TemplateVariableDefinition(
            name=name, tag=tag, default_value=default_value
        )
