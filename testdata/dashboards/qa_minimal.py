from dashboards.shared import get_dashboard_desc_template

from libddog.dashboards import Dashboard


def get_dashboard() -> Dashboard:
    dashboard = Dashboard(
        title="libddog QA: exercise dashboard lifecycle",
        desc=get_dashboard_desc_template(),
    )

    return dashboard
