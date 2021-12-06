from typing import List

from dashboards import qa_layouts, qa_metrics, qa_minimal, qa_widgets

from libddog.dashboards import Dashboard


def get_dashboards() -> List[Dashboard]:
    dashes = [
        qa_layouts.get_dashboard(),
        qa_metrics.get_dashboard(),
        qa_minimal.get_dashboard(),
        qa_widgets.get_dashboard(),
    ]

    return dashes
