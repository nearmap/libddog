from typing import List

from qa_dashboards import qa_widgets

from libddog.dashboards import Dashboard


def get_dashboards() -> List[Dashboard]:
    dashes = [
        qa_widgets.get_dashboard(),
    ]

    return dashes
