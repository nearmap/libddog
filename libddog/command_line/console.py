import sys
from typing import Any

from libddog.crud.errors import AbstractCrudError


class ConsoleWriter:
    def __init__(self, color_output: bool = True) -> None:
        self.color_output = color_output

    def errorln(self, msg: str) -> None:
        line = msg

        if not line.endswith("\n"):
            line = f"{line}\n"

        if self.color_output:
            # in yellow
            line = f"\033[33m" + line + "\033[0m"

        sys.stderr.write(line)
        sys.stderr.flush()

    def print(self, msg: str, *args: Any) -> None:
        if args:
            msg = msg % args

        sys.stderr.write(msg)
        sys.stderr.flush()

    def println(self, msg: str, *args: Any) -> None:
        if not msg.endswith("\n"):
            msg = f"{msg}\n"

        self.print(msg, *args)

    def report_failed(self, exc: AbstractCrudError) -> None:
        msg = exc.format_expanded()
        self.errorln(msg)
