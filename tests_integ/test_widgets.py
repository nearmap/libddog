import sys
from datetime import datetime

from libddog.crud import DashboardManager
from libddog.dashboards import Dashboard


class Helper:
    def __init__(self) -> None:
        self.mgr = DashboardManager()
        self.mgr.load_credentials_from_environment()

    def assign_id(self, dashboard: Dashboard) -> str:
        all_dashboards = self.mgr.list()

        existing_id: str = ""
        for dash in all_dashboards:
            if dash["title"] == dashboard.title:
                existing_id = dash["id"]
                return existing_id

        # TODO: else create a new dash so we can use that id
        return ""

    def update(self, dashboard: Dashboard, id: str) -> None:
        dt = datetime.now()
        dashboard.desc += f"\n\nLast updated during test run on: *{dt.ctime()}*"

        self.mgr.update(dashboard, id)


def test_update_all() -> None:
    sys.path.append("testdata")
    from qa_dashboards import qa_widgets

    dashboard: Dashboard = qa_widgets.get_dashboard()

    helper = Helper()

    dash_id = helper.assign_id(dashboard)
    print(f"Using id: {dash_id}")

    helper.update(dashboard, dash_id)
