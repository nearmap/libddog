from datetime import datetime
from pathlib import Path

from libddog.command_line.dashboards import DashboardManagerCli
from libddog.crud import DashboardManager
from libddog.dashboards import Dashboard


class QADashboardManager:
    def __init__(self) -> None:
        proj_root = Path(__file__).parent.parent
        testdata_dir = proj_root.joinpath("testdata").absolute()
        self.cli = DashboardManagerCli(proj_path=testdata_dir)

        self.mgr = DashboardManager()
        self.mgr.load_credentials_from_environment()

    def load_definition_by_title(self, title: str) -> Dashboard:
        dashboards = self.cli.load_definitions()
        for dashboard in dashboards:
            if dashboard.title == title:
                return dashboard

        raise RuntimeError("Failed to get dashboard with title: %s" % title)

    def assign_id_to_dashboard(self, dashboard: Dashboard) -> str:
        all_dashboards = self.mgr.list()

        existing_id: str = ""
        for dash in all_dashboards:
            if dash["title"] == dashboard.title:
                existing_id = dash["id"]
                return existing_id

        # TODO: else create a new dash so we can use that id
        raise NotImplementedError

    def update_live_dashboard(self, dashboard: Dashboard, id: str) -> None:
        dt = datetime.now()
        dashboard.desc = dashboard.desc % {"test_run_time": dt.ctime()}

        self.mgr.update(dashboard, id)
