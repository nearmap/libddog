import fnmatch
import importlib
import os
import sys
from types import ModuleType
from typing import Any, List, Optional, Union

from libddog.command_line.errors import ExceptionState
from libddog.crud.client import DatadogClient
from libddog.dashboards.components import Request
from libddog.dashboards.dashboards import Dashboard
from libddog.dashboards.widgets import Group, Widget
from libddog.metrics.query import QueryMonad
from libddog.tools.timekeeping import parse_date, time_since, utcnow


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


def count_queries(obj: Union[Dashboard, Widget, Request, QueryMonad]) -> int:
    if isinstance(obj, Dashboard):
        return sum([count_queries(w) for w in obj.widgets])
    elif isinstance(obj, Group):
        return sum([count_queries(w) for w in obj.widgets])
    elif isinstance(obj, Widget):
        return sum([count_queries(req) for req in getattr(obj, "requests", [])])
    elif isinstance(obj, Request):
        return sum([count_queries(q) for q in obj.queries])
    elif isinstance(obj, QueryMonad):
        return 1


class CommandLineError(Exception):
    def __init__(
        self, msg: str, *args: object, exc: Optional[Exception] = None
    ) -> None:
        super().__init__()

        self.msg = msg
        self.args = args
        self.exc = exc

        # if we're in an exception context then save the state
        self.exc_state = ExceptionState.create()

    @property
    def message(self) -> str:
        return self.msg % self.args


class ConsoleWriter:
    def __init__(self) -> None:
        pass

    def errorln(self, msg: str, *args: Any, exc: Optional[Exception] = None) -> None:
        exc_state = None
        if args:
            msg = msg % args

        if exc:
            msg = f"{msg}: {exc!r}"

            # if we have a saved traceback then use it
            if isinstance(exc, CommandLineError):
                exc_state = exc.exc_state

        # if we don't have a traceback try to extract it now
        if not exc_state:
            exc_state = ExceptionState.create()

        line = f"{msg}\n"
        sys.stderr.write(line)

        if exc_state:
            exc_state.print(file=sys.stderr)

        sys.stderr.flush()

    println = errorln


class DashboardManagerCli:
    def __init__(self, proj_path: str) -> None:
        self.proj_path = os.path.abspath(proj_path)
        self.writer = ConsoleWriter()

        self.containing_dir = "config"
        self.definition_module = "dashboards"
        self.import_path = f"{self.containing_dir}.{self.definition_module}"

        self._dashboard_manager: Optional[DatadogClient] = None  # lazy attribute

    @property
    def dashboard_manager(self) -> DatadogClient:
        if self._dashboard_manager is None:
            self._dashboard_manager = DatadogClient()
            self._dashboard_manager.load_credentials_from_environment()

        return self._dashboard_manager

    def load_definitions_module(self) -> ModuleType:
        # add '.' to sys.path to make 'config' importable
        if self.proj_path not in sys.path:
            sys.path.append(self.proj_path)

        # import the module
        try:
            dashes_module = importlib.import_module(self.import_path)
        except ModuleNotFoundError:
            raise CommandLineError(
                "Failed to import definition module %r", self.import_path
            )

        # try calling get_dashboards
        try:
            dashes = dashes_module.get_dashboards()  # type: ignore
            for dash in dashes:
                if not isinstance(dash, Dashboard):
                    raise TypeError("Value returned was not a Dashboard: %r" % dash)
        except Exception as exc:
            raise CommandLineError(
                "Failed call to get_dashboards() in definition module at %r",
                self.import_path,
                exc=exc,
            )

        return dashes_module

    def load_definitions(self) -> List[Dashboard]:
        module = self.load_definitions_module()
        dashes: List[Dashboard] = module.get_dashboards()  # type: ignore
        return dashes

    def filter_definitions(
        self, pattern: str, dashes: List[Dashboard]
    ) -> List[Dashboard]:
        return [dash for dash in dashes if fnmatch.fnmatch(dash.title, pattern)]

    def list_definitions(self) -> None:
        dashes = self.load_definitions()
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

    def list_live(self) -> None:
        fmt = "%11s  %20s  %9s  %9s  %s"
        header_cols = (
            "ID",
            "AUTHOR",
            "CREATED",
            "MODIFIED",
            "TITLE",
        )
        self.writer.println(fmt, *header_cols)

        dashboard_dcts = self.dashboard_manager.list()

        tuples = []
        for dct in dashboard_dcts:
            modified_at = parse_date(dct["modified_at"])
            modified_ago = utcnow() - modified_at
            tuples.append((modified_ago, dct))

        # sort by oldest modified time first
        tuples.sort(reverse=True)

        for modified_ago, dct in tuples:
            id = dct["id"]
            author_handle = dct["author_handle"]
            title = dct["title"]
            created_at = parse_date(dct["created_at"])
            created_ago = utcnow() - created_at

            # user@company.com -> user
            author_handle = author_handle.split("@")[0]

            cols = (
                id,
                author_handle,
                time_since(created_ago),
                time_since(modified_ago),
                title,
            )
            self.writer.println(fmt, *cols)

        self.writer.println("%d dashboards found" % len(tuples))

    def update_live(self, *, title_pat: str, dry_run: bool = False) -> None:
        dashes = self.load_definitions()
        dashes = self.filter_definitions(title_pat, dashes)

        verb = "Updating" if not dry_run else "Dry run: Updating"

        for dash in dashes:
            msg = f"{verb} dashboard {dash.id!r} entitled {dash.title!r}"
            self.writer.println(msg)

            if dry_run:
                continue

            self.dashboard_manager.update(dash)
