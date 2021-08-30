import contextlib
import sys

from libddog.command_line.dashboards import DashboardManagerCli


@contextlib.contextmanager
def ensure_module_is_unloaded():
    names = ["config.dashboards", "config"]

    try:
        yield

    finally:
        for name in names:
            if name in sys.modules:
                del sys.modules[name]


EXPECTED_VALID_DEFS_OUTPUT = """\
ID           GROUPS  WIDGETS  QUERIES  TITLE
None              4       60       63  libddog QA: exercise metrics queries
None              1        5        5  libddog QA: exercise widgets
"""


def test__valid_defs(capsys) -> None:
    proj_path = "testdata"
    manager = DashboardManagerCli(proj_path, use_color_output=False)

    with ensure_module_is_unloaded():
        manager.list_defs()

    captured = capsys.readouterr()
    assert captured.err == EXPECTED_VALID_DEFS_OUTPUT


def test__invalid_defs__misnamed_config_dir(capsys) -> None:
    proj_path = "testdata/invalid_cases/misnamed_config_dir"
    manager = DashboardManagerCli(proj_path, use_color_output=False)

    manager.list_defs()

    captured = capsys.readouterr()
    assert captured.err == (
        "DashboardDefinitionsImportError: Failed to import definitions "
        "module 'config.dashboards': No module named 'config'\n"
    )


def test__invalid_defs__misnamed_dashboards_file(capsys) -> None:
    proj_path = "testdata/invalid_cases/misnamed_dashboards_file"
    manager = DashboardManagerCli(proj_path, use_color_output=False)

    manager.list_defs()

    captured = capsys.readouterr()
    assert captured.err == (
        "DashboardDefinitionsImportError: Failed to import definitions "
        "module 'config.dashboards': No module named 'config.dashboards'\n"
    )
