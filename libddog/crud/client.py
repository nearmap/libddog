import os
from typing import Any, List, Optional

import datadog
import datadog.api

from libddog.common.types import JsonDict
from libddog.crud.errors import (
    DashboardCreateFailed,
    DashboardDeleteFailed,
    DashboardGetFailed,
    DashboardListFailed,
    DashboardUpdateFailed,
    MissingDatadogApiKey,
    MissingDatadogAppKey,
)
from libddog.dashboards import Dashboard


class DatadogClient:
    env_varname_api_key = "DATADOG_API_KEY"
    env_varname_app_key = "DATADOG_APPLICATION_KEY"

    def load_credentials_from_environment(self) -> None:
        var_api_key = self.env_varname_api_key
        var_app_key = self.env_varname_app_key

        api_key = os.getenv(var_api_key)
        app_key = os.getenv(var_app_key)

        if not api_key:
            error = f"Could not find {var_api_key!r} set in the environment"
            raise MissingDatadogApiKey(errors=[error])

        if not app_key:
            error = f"Could not find {var_app_key!r} set in the environment"
            raise MissingDatadogAppKey(errors=[error])

        options = {
            "api_key": api_key,
            "app_key": app_key,
        }
        datadog.initialize(**options)  # type: ignore

    def parse_response_errors(self, resp: Any) -> List[str]:
        if type(resp) == dict:
            return resp.get("errors") or []

        return []

    def create_dashboard(self, dashboard: Dashboard) -> str:
        client_kwargs = dashboard.as_dict()
        client_kwargs.pop("id", None)  # we cannot pass an id when creating

        resp = datadog.api.Dashboard.create(**client_kwargs)  # type: ignore
        errors = self.parse_response_errors(resp)
        if errors:
            raise DashboardCreateFailed(errors=errors)

        id: str = resp["id"]
        return id

    def delete_dashboard(self, *, id: str) -> None:
        result = datadog.api.Dashboard.delete(id=id)  # type: ignore

        errors = self.parse_response_errors(result)
        if errors:
            raise DashboardDeleteFailed(errors=errors)

    def get_dashboard(self, *, id: str) -> JsonDict:
        result = datadog.api.Dashboard.get(id=id)  # type: ignore

        errors = self.parse_response_errors(result)
        if errors:
            raise DashboardGetFailed(errors=errors)

        assert isinstance(result, dict)  # help mypy
        return result

    def list_dashboards(self) -> List[JsonDict]:
        result = datadog.api.Dashboard.get_all()  # type: ignore

        errors = self.parse_response_errors(result)
        if errors:
            raise DashboardListFailed(errors=errors)

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

        resp = datadog.api.Dashboard.update(id=id, **client_kwargs)  # type: ignore
        errors = self.parse_response_errors(resp)
        if errors:
            raise DashboardUpdateFailed(errors=errors)
