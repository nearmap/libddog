import fnmatch
import os
from typing import Any, List, Union

from libddog.command_line.console import ConsoleWriter
from libddog.crud.dashboards import DashboardManager
from libddog.crud.errors import AbstractCrudError
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


class DashboardManagerCli:
    def __init__(self, proj_path: str) -> None:
        self.proj_path = os.path.abspath(proj_path)

        self.writer = ConsoleWriter()
        self.manager = DashboardManager(self.proj_path)

    def filter_definitions(
        self, pattern: str, dashes: List[Dashboard]
    ) -> List[Dashboard]:
        return [dash for dash in dashes if fnmatch.fnmatch(dash.title, pattern)]

    def delete_live(self, *, id: str) -> int:
        # Take a snapshot first to make restoring it possible
        exit_code = self.snapshot_live(id=id)
        if exit_code != os.EX_OK:
            return exit_code

        self.writer.print("Deleting live dashboard with id: %r... ", id)

        try:
            self.manager.delete_dashboard(id=id)
            self.writer.println("done")

        except AbstractCrudError as exc:
            self.writer.report_failed(exc)
            return os.EX_UNAVAILABLE

        return os.EX_OK

    def list_defs(self) -> int:
        dashes = None

        try:
            dashes = self.manager.load_definitions()

        except AbstractCrudError as exc:
            self.writer.report_failed(exc)
            return os.EX_UNAVAILABLE

        fmt = "%6s  %7s  %7s  %s"
        self.writer.println(fmt, "GROUPS", "WIDGETS", "QUERIES", "TITLE")

        # sort by title
        dashes = sorted(dashes, key=lambda dash: dash.title.lower())

        for dash in dashes:
            n_widgets = count_widgets(dash)
            n_groups = count_groups(dash)
            n_queries = count_queries(dash)

            self.writer.println(
                fmt,
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

        fmt = "%11s  %24s  %4s  %7s  %s"
        header_cols = (
            "ID",
            "USER",
            "TIME",
            "LIBDDOG",
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
            desc = dct.get("description") or ""
            user_handle = dct["author_handle"]
            user_symbol = "c"
            tool_ver = "-"
            title = dct["title"]

            # try to detect modifying user email in the description
            match = self.manager._rx_desc_user.search(desc)
            if match:
                user_email = match.group("user")
                if "@" in user_email:
                    user_handle = user_email
                    user_symbol = "m"

            # user@company.com -> user
            user_handle = user_handle.split("@")[0]
            user_handle = f"{user_handle} [{user_symbol}]"

            # detect our own fingerprint in the description
            match = self.manager._rx_desc_version.search(desc)
            if match:
                version = match.group("version")
                if version.endswith("."):
                    version = version[:-1]
                tool_ver = version
            # there is no version but we know it's libddog at least
            if match is None and self.manager._libddog_proj_name in desc:
                tool_ver = "?"

            cols = (
                id,
                user_handle,
                time_since(modified_ago),
                tool_ver,
                title,
            )
            self.writer.println(fmt, *cols)

        self.writer.println("%d dashboards found" % len(tuples))

        return os.EX_OK

    def publish_draft(self, *, title_pat: str) -> int:
        dashes = self.manager.load_definitions()
        dashes = self.filter_definitions(title_pat, dashes)

        if not dashes:
            self.writer.println(
                "Title pattern %r did not match any dashboards", title_pat
            )
            return os.EX_USAGE

        if len(dashes) > 1:
            fmt = "\n".join([f"- {dash.title}" for dash in dashes])
            self.writer.println(
                "Title pattern %r matched multiple dashboards:\n%s", title_pat, fmt
            )
            return os.EX_USAGE

        dash = dashes[0]
        dash.title = self.manager.get_draft_title(dash)
        existing = self.manager.find_first_dashboard_with_title(dash.title)

        if existing:
            id = existing["id"]

            self.writer.print(
                f"Updating dashboard with id: {id!r} entitled: {dash.title!r}... "
            )
            try:
                self.manager.update_dashboard(dashboard=dash, id=id)
                self.writer.println("done")

            except AbstractCrudError as exc:
                self.writer.report_failed(exc)
                return os.EX_IOERR

        else:
            self.writer.print(f"Creating dashboard entitled: {dash.title!r}... ")
            try:
                id = self.manager.create_dashboard(dashboard=dash)
                self.writer.println("created with id: %r", id)

            except AbstractCrudError as exc:
                self.writer.report_failed(exc)
                return os.EX_IOERR

        return os.EX_OK

    def publish_live(self, *, title_pat: str) -> int:
        dashes = self.manager.load_definitions()
        dashes = self.filter_definitions(title_pat, dashes)

        for dash in dashes:
            existing = self.manager.find_first_dashboard_with_title(dash.title)

            if existing:
                id = existing["id"]

                # Take a snapshot first to make restoring it possible
                exit_code = self.snapshot_live(id=id)
                if exit_code != os.EX_OK:
                    return exit_code

                self.writer.print(
                    f"Updating dashboard with id: {id!r} entitled: {dash.title!r}... "
                )

                try:
                    self.manager.update_dashboard(dashboard=dash, id=id)
                    self.writer.println("done")

                except AbstractCrudError as exc:
                    self.writer.report_failed(exc)
                    return os.EX_IOERR

            else:
                self.writer.print(f"Creating dashboard entitled: {dash.title!r}... ")

                try:
                    id = self.manager.create_dashboard(dashboard=dash)
                    self.writer.println("created with id: %r", id)

                except AbstractCrudError as exc:
                    self.writer.report_failed(exc)
                    return os.EX_IOERR

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
