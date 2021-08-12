from tests_integ.tools import QADashboardManager


def test_put_and_get_metrics() -> None:
    mgr = QADashboardManager()
    dashboard = mgr.load_definition_by_title("libddog QA: exercise metrics queries")

    dash_id = mgr.assign_id_to_dashboard(dashboard)
    mgr.timestamp_dashboard(dashboard)

    mgr.update_live_dashboard(dashboard, dash_id)


def test_put_and_get_widgets() -> None:
    mgr = QADashboardManager()
    dashboard = mgr.load_definition_by_title("libddog QA: exercise widgets")

    dash_id = mgr.assign_id_to_dashboard(dashboard)
    mgr.timestamp_dashboard(dashboard)

    mgr.update_live_dashboard(dashboard, dash_id)
