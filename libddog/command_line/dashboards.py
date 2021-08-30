import fnmatch
import importlib
import os
import sys
from types import ModuleType
from typing import Any, Generic, List, Optional, Union

from libddog.command_line.errors import ExceptionState
from libddog.crud.client import DatadogClient
from libddog.crud.dashboards import DashboardManager
from libddog.crud.errors import AbstractCrudError, DashboardGetFailed
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

    def report_failed(self, exc: AbstractCrudError) -> None:
        msg = exc.format_expanded()
        self.red_errorln(msg)

    def red_errorln(self, msg: str) -> None:
        if not msg.endswith("\n"):
            msg = f"{msg}\n"

        line = f"\033[31m" + msg + "\033[0m"

        sys.stderr.write(line)
        sys.stderr.flush()

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

    def print(self, msg: str, *args: Any) -> None:
        if args:
            msg = msg % args

        sys.stderr.write(msg)
        sys.stderr.flush()


class DashboardManagerCli:
    def __init__(self, proj_path: str) -> None:
        self.proj_path = os.path.abspath(proj_path)
        self.writer = ConsoleWriter()

        self.manager = DashboardManager(self.proj_path)

    def filter_definitions(
        self, pattern: str, dashes: List[Dashboard]
    ) -> List[Dashboard]:
        return [dash for dash in dashes if fnmatch.fnmatch(dash.title, pattern)]

    def list_defs(self) -> int:
        dashes = None

        try:
            dashes = self.manager.load_definitions()

        except AbstractCrudError as exc:
            self.writer.report_failed(exc)
            return os.EX_UNAVAILABLE

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

        return os.EX_OK

    def list_live(self) -> int:
        dashboard_dcts = None

        try:
            dashboard_dcts = self.manager.list_dashboards()

        except AbstractCrudError as exc:
            self.writer.report_failed(exc)
            return os.EX_UNAVAILABLE

        fmt = "%11s  %20s  %9s  %9s  %s"
        header_cols = (
            "ID",
            "AUTHOR",
            "CREATED",
            "MODIFIED",
            "TITLE",
        )
        self.writer.println(fmt, *header_cols)

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

        return os.EX_OK

    def snapshot_live(self, *, id: str) -> int:
        self.writer.print("Creating snapshot of live dashboard with id: %r... ", id)

        try:
            fp = self.manager.create_snapshot(id)
            self.writer.println("saved to: %s", fp)

        except AbstractCrudError as exc:
            self.writer.report_failed(exc)
            return os.EX_UNAVAILABLE

        return os.EX_OK

    def update_live(self, *, title_pat: str, dry_run: bool = False) -> int:
        dashes = self.manager.load_definitions()
        dashes = self.filter_definitions(title_pat, dashes)

        for dash in dashes:
            self.writer.print(
                f"Updating dashboard with id: {dash.id!r} entitled: {dash.title!r}... "
            )

            if dry_run:
                self.writer.println("skipped (dry run)")
                continue

            try:
                self.manager.update_dashboard(dash)
                self.writer.println("done")

            except AbstractCrudError as exc:
                self.writer.report_failed(exc)
                return os.EX_IOERR

        return os.EX_OK
