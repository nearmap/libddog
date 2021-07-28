import importlib
import os
import sys
from types import ModuleType
from typing import List, Union

from libddog.dashboards.dashboards import Dashboard
from libddog.dashboards.widgets import Group, Widget


class CommandLineError(Exception):
    def __init__(self, msg: str, *args: object) -> None:
        super().__init__()

        self.msg = msg
        self.args = args

    @property
    def message(self):
        return self.msg % self.args


class ConsoleWriter:
    def __init__(self) -> None:
        pass

    def errorln(self, msg, *args) -> None:
        msg = msg % args
        line = f"{msg}\n"
        sys.stderr.write(line)
        sys.stderr.flush()

    println = errorln


class DashboardManager:
    def __init__(self, proj_path: str) -> None:
        self.proj_path = os.path.abspath(proj_path)
        self.writer = ConsoleWriter()

        self.containing_dir = "config"
        self.definition_module = "dashboards"
        self.import_path = f"{self.containing_dir}.{self.definition_module}"

    def load_definitions_module(self) -> ModuleType:
        try:
            dashes_module = importlib.import_module(self.import_path)
        except ModuleNotFoundError:
            raise CommandLineError(
                "Failed to import definition module at %r", self.import_path
            )

        return dashes_module

    def count_groups(self, dash: Dashboard) -> int:
        def count(obj: Union[Dashboard, Widget]) -> int:
            if isinstance(obj, Group):
                return 1 + sum([count(w) for w in obj.widgets])
            elif isinstance(obj, Widget):
                return 0
            elif isinstance(obj, Dashboard):
                return sum([count(w) for w in obj.widgets])

        return count(dash)

    def count_widgets(self, dash: Dashboard) -> int:
        def count(obj: Union[Dashboard, Widget]) -> int:
            if isinstance(obj, Group):
                return sum([count(w) for w in obj.widgets])
            elif isinstance(obj, Widget):
                return 1
            elif isinstance(obj, Dashboard):
                return sum([count(w) for w in obj.widgets])

        return count(dash)

    def list_definitions(self):
        module = self.load_definitions_module()
        dashes: List[Dashboard] = module.get_dashboards()

        fmt = "%-11s  %6s  %7s  %s"

        self.writer.println(fmt, "ID", "GROUPS", "WIDGETS", "TITLE")

        for dash in dashes:
            n_widgets = self.count_widgets(dash)
            n_groups = self.count_groups(dash)

            self.writer.println(
                fmt,
                dash.id,
                n_groups,
                n_widgets,
                dash.title,
            )
