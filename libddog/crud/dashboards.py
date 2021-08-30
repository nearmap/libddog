import importlib
import json
import os
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import List, Optional

from libddog.common.types import JsonDict
from libddog.crud.client import DatadogClient
from libddog.crud.errors import (
    DashboardDefinitionsImportError,
    DashboardDefinitionsLoadError,
)
from libddog.dashboards.dashboards import Dashboard
from libddog.tools.timekeeping import format_datetime_for_filename, utcnow


def sanitize_title_for_filename(title: str) -> str:
    # replace any non-alpha char with '_'
    title = re.sub("[^a-zA-Z0-9]", "_", title)
    return title


class DashboardManager:
    _title_sentinel = "Untitled dashboard"
    _snapshot_dirname = "_snapshots"

    _defs_containing_dir = "config"
    _defs_module_name = "dashboards"
    _defs_import_path = f"{_defs_containing_dir}.{_defs_module_name}"

    def __init__(self, proj_path: str) -> None:
        self.proj_path = proj_path
        self.snapshots_path: Path = Path(self.proj_path) / Path(self._snapshot_dirname)

        self._client: Optional[DatadogClient] = None  # lazy attribute

    @property
    def client(self) -> DatadogClient:
        if self._client is None:
            self._client = DatadogClient()
            self._client.load_credentials_from_environment()

        return self._client

    def load_definitions_module(self) -> ModuleType:
        # add proj_path to sys.path to make 'config' importable
        if self.proj_path not in sys.path:
            sys.path.append(self.proj_path)

        import_path = self._defs_import_path
        load_func = "get_dashboards"

        # import the module
        try:
            dashes_module = importlib.import_module(import_path)
        except ModuleNotFoundError as exc:
            error = (
                f"Failed to import definitions module "
                f"{import_path!r}: {exc.args[0]}"
            )
            raise DashboardDefinitionsImportError(errors=[error])

        # probe for get_dashboards()
        get_dashboards = getattr(dashes_module, load_func, None)
        if get_dashboards is None or not callable(get_dashboards):
            error = (
                f"Definitions module {self._defs_import_path!r} "
                f"does not contain {load_func!r} function"
            )
            raise DashboardDefinitionsLoadError(errors=[error])

        # try calling get_dashboards
        dashes = get_dashboards()

        errors = []
        if not isinstance(dashes, list):
            error = f"{load_func!r} did not return a list of Dashboard instances"
            errors.append(error)

        if not errors:
            for idx, dash in enumerate(dashes):
                if not isinstance(dash, Dashboard):
                    error = f"{idx}th value returned was not a Dashboard: {dash!r}"
                    errors.append(error)

        if errors:
            raise DashboardDefinitionsLoadError(errors=[error])

        return dashes_module

    def load_definitions(self) -> List[Dashboard]:
        module = self.load_definitions_module()
        dashes: List[Dashboard] = module.get_dashboards()  # type: ignore
        return dashes

    def ensure_snapshot_path_exists(self) -> None:
        if not os.path.exists(self.snapshots_path):
            os.makedirs(self.snapshots_path)

    def create_snapshot(self, id: str) -> Path:
        self.ensure_snapshot_path_exists()

        dct = self.client.get_dashboard(id=id)

        title = dct.get("title", self._title_sentinel)
        title = sanitize_title_for_filename(title)
        date = format_datetime_for_filename(utcnow())

        block = json.dumps(dct, indent=2, sort_keys=True)
        fn = Path(f"{id}--{title}--{date}.json")
        fp = self.snapshots_path / fn

        with open(fp, "w") as fl:
            fl.write(block)
            fl.write("\n")

        return fp

    def get_dashboard(self, *, id: str) -> JsonDict:
        return self.client.get_dashboard(id=id)

    def list_dashboards(self) -> List[JsonDict]:
        return self.client.list_dashboards()

    def update_dashboard(self, dashboard: Dashboard, id: Optional[str] = None) -> None:
        self.client.update_dashboard(dashboard=dashboard, id=id)
