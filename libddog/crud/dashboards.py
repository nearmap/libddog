import json
import os
import re
from pathlib import Path
from typing import Optional

from libddog.crud.client import DatadogClient
from libddog.tools.timekeeping import format_datetime_for_filename, utcnow


def sanitize_title(title: str) -> str:
    # replace any non-alpha char with '_'
    title = re.sub("[^a-zA-Z0-9]", "_", title)
    return title


class DashboardManager:
    _title_sentinel = "Untitled dashboard"
    _snapshot_dirname = "_snapshots"

    def __init__(self) -> None:
        self.proj_path = Path(__file__).parent.parent.parent
        self.snapshots_path = self.proj_path / Path(self._snapshot_dirname)

        self._client: Optional[DatadogClient] = None  # lazy attribute

    @property
    def client(self) -> DatadogClient:
        if self._client is None:
            self._client = DatadogClient()
            self._client.load_credentials_from_environment()

        return self._client

    def ensure_snapshot_path_exists(self) -> None:
        if not os.path.exists(self.snapshots_path):
            os.makedirs(self.snapshots_path)

    def create_snapshot(self, id: str) -> Path:
        self.ensure_snapshot_path_exists()

        dct = self.client.get_dashboard(id=id)

        title = dct.get("title", self._title_sentinel)
        title = sanitize_title(title)
        date = format_datetime_for_filename(utcnow())

        block = json.dumps(dct, indent=2, sort_keys=True)
        fn = Path(f"{id}--{title}--{date}.json")
        fp = self.snapshots_path / fn

        with open(fp, "w") as fl:
            fl.write(block)
            fl.write("\n")

        return fp
