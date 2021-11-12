import json
import logging
import os
import time
from typing import Dict, List, Optional, Type

import requests

from libddog.common.types import JsonDict
from libddog.crud.errors import (
    AbstractCrudError,
    DashboardCreateFailed,
    DashboardDeleteFailed,
    DashboardGetFailed,
    DashboardListFailed,
    DashboardUpdateFailed,
    MissingDatadogApiKey,
    MissingDatadogAppKey,
)
from libddog.dashboards import Dashboard
from libddog.tools.logs import enable_logging


class DatadogClient:
    env_varname_api_key = "DATADOG_API_KEY"
    env_varname_app_key = "DATADOG_APPLICATION_KEY"

    def __init__(self) -> None:
        self.api_key: Optional[str] = None
        self.app_key: Optional[str] = None

        self.baseurl = "https://api.datadoghq.com/api/v1"

        self.session = requests.Session()

        self.logger = logging.getLogger(__name__)

        # Force enable logging because we want to see our own log messages. This
        # is not the greatest solution; ideally this should be done at the
        # entrypoint to the program. But we have different code paths that lead
        # us here, so doing this purely in bin/ddog would not affect logging in
        # tests and different tests may wish to consume the client at different
        # layers. Doing this at the innermost layer where we know logging is
        # definitely used is the easiest way to avoid missing code paths.
        # We need to force enable because at this point it's likely that some
        # other library has init'd logging already with a different set of
        # parameters.
        enable_logging(force=True)

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

        self.api_key = api_key
        self.app_key = app_key

    def prepare_headers(self) -> Dict[str, str]:
        assert self.api_key is not None
        assert self.app_key is not None

        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
        }
        return headers

    def build_dashboard_url(self, id: Optional[str] = None) -> str:
        url = f"{self.baseurl}/dashboard"

        if id is not None:
            url = f"{url}/{id}"

        return url

    def try_parse_json_payload(self, response: requests.Response) -> Optional[JsonDict]:
        try:
            payload: JsonDict = response.json()
            return payload
        except json.decoder.JSONDecodeError:
            pass

        return None

    def try_parse_payload_errors(self, payload: Optional[JsonDict]) -> List[str]:
        if isinstance(payload, dict):
            return payload.get("errors") or []

        return []

    def try_parse_ratelimit_reset(self, response: requests.Response) -> Optional[float]:
        value = response.headers.get("X-RateLimit-Reset")

        if value:
            try:
                return float(value)
            except ValueError:
                pass

        return None

    def make_request(
        self,
        *,
        request: requests.Request,
        expected_code: int,
        exc_cls: Type[AbstractCrudError],
    ) -> Optional[JsonDict]:
        response: Optional[requests.Response] = None
        payload: Optional[JsonDict] = None
        errors: List[str] = []

        attempt_no = 1
        wait_secs_base = 0.5
        prepared_request = request.prepare()

        while attempt_no < 4:
            try:
                response = self.session.send(prepared_request)
            except requests.exceptions.RequestException as exc:
                errors.append(str(exc))

            if response is not None and response.status_code == 429:
                wait_secs = self.try_parse_ratelimit_reset(response)
                if wait_secs is None:
                    # there is no jitter here but I don't think it matters
                    # because this is a fallback code path anyway
                    wait_secs = wait_secs_base * (2 ** attempt_no)

                # log a warning because we are deliberately pausing execution
                self.logger.warning(
                    f"Request was rate limited by the Datadog API, "
                    f"retrying in {wait_secs} seconds"
                )
                time.sleep(wait_secs)
                attempt_no += 1
                continue

            break

        if response is not None:
            payload = self.try_parse_json_payload(response)
            errors = self.try_parse_payload_errors(payload) or []

        if response is None or response.status_code != expected_code or errors:
            status_code = response.status_code if response is not None else None
            raise exc_cls(errors=errors, http_status_code=status_code)

        return payload

    def create_dashboard(self, dashboard: Dashboard) -> str:
        client_kwargs = dashboard.as_dict()
        client_kwargs.pop("id", None)  # we cannot pass an id when creating

        url = self.build_dashboard_url()
        headers = self.prepare_headers()
        request = requests.Request(
            method="POST", url=url, headers=headers, json=client_kwargs
        )

        payload = self.make_request(
            request=request, expected_code=200, exc_cls=DashboardCreateFailed
        )

        assert isinstance(payload, dict)  # help mypy
        id = payload["id"]
        assert isinstance(id, str)  # help mypy

        return id

    def delete_dashboard(self, *, id: str) -> None:
        url = self.build_dashboard_url(id=id)
        headers = self.prepare_headers()
        request = requests.Request(method="DELETE", url=url, headers=headers)

        self.make_request(
            request=request, expected_code=200, exc_cls=DashboardDeleteFailed
        )

    def get_dashboard(self, *, id: str) -> JsonDict:
        url = self.build_dashboard_url(id=id)
        headers = self.prepare_headers()
        request = requests.Request(method="GET", url=url, headers=headers)

        payload = self.make_request(
            request=request, expected_code=200, exc_cls=DashboardGetFailed
        )

        assert isinstance(payload, dict)  # help mypy
        return payload

    def list_dashboards(self) -> List[JsonDict]:
        url = self.build_dashboard_url()
        headers = self.prepare_headers()
        request = requests.Request(method="GET", url=url, headers=headers)

        payload = self.make_request(
            request=request, expected_code=200, exc_cls=DashboardListFailed
        )

        assert isinstance(payload, dict)  # help mypy
        dashboards = payload["dashboards"]
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

        url = self.build_dashboard_url(id=id)
        headers = self.prepare_headers()
        request = requests.Request(
            method="PUT", url=url, headers=headers, json=client_kwargs
        )

        self.make_request(
            request=request, expected_code=200, exc_cls=DashboardUpdateFailed
        )
