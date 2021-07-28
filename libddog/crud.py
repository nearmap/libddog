import os
import pprint
from typing import Any, Optional

import datadog

from libddog.dashboards import Dashboard


class DashboardManager:
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

    def get(self, id: str) -> Any:
        result = datadog.api.Dashboard.get(id=id)  # type: ignore
        return result

    def list(self) -> Any:
        result = datadog.api.Dashboard.get_all()  # type: ignore
        return result["dashboards"]

    def update(self, dashboard: Dashboard) -> None:
        if not dashboard.id:
            raise RuntimeError(
                "Cannot update dashboard without an .id attribute: %r" % dashboard.title
            )

        client_kwargs = dashboard.as_kwargs_to_official_client()

        try:
            resp = datadog.api.Dashboard.update(**client_kwargs)  # type: ignore
            error_strs = self.parse_response(resp)
            if error_strs:
                print(
                    "Failed to update dashboard %r entitled %r:\n%s"
                    % (dashboard.id, dashboard.title, error_strs)
                )
                pprint.pprint(client_kwargs)

            else:
                print(
                    "Updated dashboard %r entitled %r" % (dashboard.id, dashboard.title)
                )
        except Exception as exc:
            raise
