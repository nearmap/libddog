from typing import List, Optional

from libddog.dashboards.dashboards import Dashboard


class AbstractCrudError(Exception):
    def __init__(self, errors: Optional[List[str]] = None) -> None:
        self.errors = errors or []

    def format_expanded(self) -> str:
        prefix = self.__class__.__name__

        if not self.errors:
            return prefix

        if len(self.errors) == 1:
            return f"{prefix}: {self.errors[0]}"

        block = "\n".join([f"- {msg}" for msg in self.errors])
        return f"{prefix}:\n{block}\n"


class DashboardGetFailed(AbstractCrudError):
    def __init__(self, id: str, errors: Optional[List[str]] = None) -> None:
        super().__init__(errors)

        self.id = id


class DashboardUpdateFailed(AbstractCrudError):
    def __init__(
        self, id: str, dashboard: Dashboard, errors: Optional[List[str]] = None
    ) -> None:
        super().__init__(id)

        self.id = id
        self.dashboard = dashboard
        self.errors = errors or []
