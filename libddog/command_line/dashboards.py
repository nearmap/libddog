import importlib
import os
import sys
from types import ModuleType
from typing import Any, List, Tuple, Union

from libddog.dashboards.components import Request
from libddog.dashboards.dashboards import Dashboard
from libddog.dashboards.widgets import Group, Widget
from libddog.metrics.query import Query


def count_groups(obj: Union[Dashboard, Widget]) -> int:
    if isinstance(obj, Dashboard):
        return sum([count_groups(w) for w in obj.widgets])
    elif isinstance(obj, Group):
        return 1 + sum([count_groups(w) for w in obj.widgets])
    elif isinstance(obj, Widget):
        return 0


def count_widgets(obj: Union[Dashboard, Widget]) -> int:
    if isinstance(obj, Dashboard):
        return sum([count_widgets(w) for w in obj.widgets])
    elif isinstance(obj, Group):
        return sum([count_widgets(w) for w in obj.widgets])
    elif isinstance(obj, Widget):
        return 1


def count_queries(obj: Union[Dashboard, Widget, Request, Query]) -> int:
    if isinstance(obj, Dashboard):
        return sum([count_queries(w) for w in obj.widgets])
    elif isinstance(obj, Group):
        return sum([count_queries(w) for w in obj.widgets])
    elif isinstance(obj, Widget):
        return sum([count_queries(req) for req in getattr(obj, "requests", [])])
    elif isinstance(obj, Request):
        return sum([count_queries(q) for q in obj.queries])
    elif isinstance(obj, Query):
        return 1


class CommandLineError(Exception):
    def __init__(self, msg: str, *args: object) -> None:
        super().__init__()

        self.msg = msg
        self.args = args

    @property
    def message(self) -> str:
        return self.msg % self.args


class ConsoleWriter:
    def __init__(self) -> None:
        pass

    def errorln(self, msg: str, *args: Any) -> None:
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

    def list_definitions(self) -> None:
        module = self.load_definitions_module()
        dashes: List[Dashboard] = module.get_dashboards()

        fmt = "%-11s  %6s  %7s  %7s  %s"

        self.writer.println(fmt, "ID", "GROUPS", "WIDGETS", "QUERIES", "TITLE")

        for dash in dashes:
            n_widgets = count_widgets(dash)
            n_groups = count_groups(dash)
            n_queries = count_queries(dash)

            self.writer.println(
                fmt,
                dash.id,
                n_groups,
                n_widgets,
                n_queries,
                dash.title,
            )
