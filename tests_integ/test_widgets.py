from typing import List

from libtests.managers import QADashboardManager
from libtests.matchers import PatchInstruction, assign, obj_matcher

PATCHES: List[PatchInstruction] = [
    assign('.["author_handle"]', "author-handle"),
    assign('.["author_name"]', "author-name"),
    assign('.["created_at"]', "created-at"),
    assign('.["id"]', "id"),
    assign('.["modified_at"]', "modified-at"),
    assign('.["restricted_roles"]', []),
    assign('.["url"]', "url"),
    # group id -or- widget id outside group
    assign('.["widgets"][]["id"]', "id"),
    # widget id inside group
    assign('.["widgets"][]["definition"]["widgets"][]["id"]', "id"),
]


def test_put_and_get_metrics() -> None:
    mgr = QADashboardManager()
    dashboard = mgr.load_definition_by_title("libddog QA: exercise metrics queries")

    dash_id = mgr.assign_id_to_dashboard(dashboard)

    # put the dashboard
    mgr.update_live_dashboard(dashboard, dash_id)

    # now read it back and assert that it matches our model
    expected = dashboard.as_dict()
    actual = mgr.manager.get_dashboard(id=dash_id)

    assert obj_matcher(expected, PATCHES) == obj_matcher(actual, PATCHES)


def test_put_and_get_widgets() -> None:
    mgr = QADashboardManager()
    dashboard = mgr.load_definition_by_title("libddog QA: exercise widgets")

    dash_id = mgr.assign_id_to_dashboard(dashboard)

    # put the dashboard
    mgr.update_live_dashboard(dashboard, dash_id)

    # now read it back and assert that it matches our model
    expected = dashboard.as_dict()
    actual = mgr.manager.get_dashboard(id=dash_id)

    assert obj_matcher(expected, PATCHES) == obj_matcher(actual, PATCHES)


def test_put_and_get_layouts() -> None:
    mgr = QADashboardManager()
    dashboard = mgr.load_definition_by_title("libddog QA: exercise layouts")

    dash_id = mgr.assign_id_to_dashboard(dashboard)

    # put the dashboard
    mgr.update_live_dashboard(dashboard, dash_id)

    # now read it back and assert that it matches our model
    expected = dashboard.as_dict()
    actual = mgr.manager.get_dashboard(id=dash_id)

    assert obj_matcher(expected, PATCHES) == obj_matcher(actual, PATCHES)


def test_dashboard_lifecycle() -> None:
    mgr = QADashboardManager()
    dashboard = mgr.load_definition_by_title("libddog QA: exercise dashboard lifecycle")

    payload = mgr.manager.find_first_dashboard_with_title(dashboard.title)
    if payload:
        dash_id = payload["id"]
        mgr.manager.delete_dashboard(id=dash_id)

    dash_id = mgr.manager.create_dashboard(dashboard)
    mgr.manager.get_dashboard(id=dash_id)
    mgr.manager.update_dashboard(dashboard, id=dash_id)
    mgr.manager.delete_dashboard(id=dash_id)
