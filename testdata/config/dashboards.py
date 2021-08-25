from typing import List

from dashboards import qa_metrics, qa_widgets

from libddog.dashboards import Dashboard


def get_dashboards() -> List[Dashboard]:
    dashes = [
        qa_metrics.get_dashboard(),
        qa_widgets.get_dashboard(),
    ]

    return dashes
