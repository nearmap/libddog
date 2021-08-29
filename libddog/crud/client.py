import os
import pprint
from typing import Any, List, Optional

import datadog
import datadog.api

from libddog.common.types import JsonDict
from libddog.dashboards import Dashboard


class DatadogClient:
    env_varname_api_key = "DATADOG_API_KEY"
    env_varname_app_key = "DATADOG_APPLICATION_KEY"

    def load_credentials_from_environment(self) -> None:
        api_key = os.getenv(self.env_varname_api_key)
        app_key = os.getenv(self.env_varname_app_key)

        if not api_key:
            raise RuntimeError(
                "Could not find %r set in the environment" % self.env_varname_api_key
            )
        if not app_key:
            raise RuntimeError(
                "Could not find %r set in the environment" % self.env_varname_app_key
            )

        options = {
            "api_key": api_key,
            "app_key": app_key,
        }
        datadog.initialize(**options)  # type: ignore

    def parse_response(self, resp: Any) -> Optional[str]:
        if type(resp) == dict:
            errors = resp.get("errors")
            if errors:
                error_strs = "\n".join(["- %s" % err for err in errors])
                return error_strs

        return None

    def get_dashboard(self, id: str) -> JsonDict:
        result = datadog.api.Dashboard.get(id=id)  # type: ignore

        assert isinstance(result, dict)  # help mypy

        return result

    def list_dashboards(self) -> List[JsonDict]:
        result = datadog.api.Dashboard.get_all()  # type: ignore

        dashboards = result["dashboards"]
        assert isinstance(dashboards, list)  # help mypy

        return dashboards

    def update_dashboard(self, dashboard: Dashboard, id: Optional[str] = None) -> None:
        id = id or dashboard.id

        if not id:
            raise ValueError(
                "Cannot update dashboard without an id: %r" % dashboard.title
            )

        client_kwargs = dashboard.as_dict()
        client_kwargs.pop("id", None)  # we pass it separately

        try:
            resp = datadog.api.Dashboard.update(id=id, **client_kwargs)  # type: ignore
            error_strs = self.parse_response(resp)
            if error_strs:
                print(
                    "Failed to update dashboard %r entitled %r:\n%s"
                    % (id, dashboard.title, error_strs)
                )
                pprint.pprint(client_kwargs)

            else:
                print("Updated dashboard %r entitled %r" % (id, dashboard.title))
        except Exception as exc:
            raise
