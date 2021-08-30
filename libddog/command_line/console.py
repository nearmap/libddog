import sys
from typing import Any, Optional

from libddog.command_line.errors import ExceptionState
from libddog.crud.errors import AbstractCrudError


class ConsoleWriter:
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
