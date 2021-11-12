from typing import List, Optional


class AbstractCrudError(Exception):
    """
    We use the name of the class as an explanatory failure code in user facing
    error messages, so derived classes should have meaningful names (and
    AbstractCrudError should not be instantiated directly).

    We use `errors` as an optional list of error strings returned by the Datadog
    API. These are meant to be details to further explain the error. If the
    error originates inside libddog we should also populate `errors` with
    explanatory causes.
    """

    def __init__(
        self,
        *,
        errors: Optional[List[str]] = None,
        http_status_code: Optional[int] = None,
    ) -> None:
        self.errors = errors or []
        self.http_status_code = http_status_code

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"http_status_code={self.http_status_code!r}, errors={self.errors!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def format_expanded(self) -> str:
        prefix = self.__class__.__name__

        # ClassName
        if not self.errors:
            return prefix

        # ClassName: the first cause of the error
        if len(self.errors) == 1:
            return f"{prefix}: {self.errors[0]}"

        # ClassName:
        # - the first cause of the error
        # - the second cause of the error
        block = "\n".join([f"- {error}" for error in self.errors])
        return f"{prefix}:\n{block}\n"


class AppKeyGetFailed(AbstractCrudError):
    pass


class AppKeyListFailed(AbstractCrudError):
    pass


class DashboardCreateFailed(AbstractCrudError):
    pass


class DashboardDeleteFailed(AbstractCrudError):
    pass


class DashboardGetFailed(AbstractCrudError):
    pass


class DashboardListFailed(AbstractCrudError):
    pass


class DashboardUpdateFailed(AbstractCrudError):
    pass


class DashboardDefinitionsImportError(AbstractCrudError):
    pass


class DashboardDefinitionsLoadError(AbstractCrudError):
    pass


class MissingDatadogApiKey(AbstractCrudError):
    pass


class MissingDatadogAppKey(AbstractCrudError):
    pass
