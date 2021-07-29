import sys
import traceback
from types import TracebackType
from typing import Optional, TextIO, Type


class ExceptionState:
    def __init__(
        self, exc_type: Type[BaseException], value: BaseException, tb: TracebackType
    ) -> None:
        self.exc_type = exc_type
        self.value = value
        self.tb = tb

    @classmethod
    def create(cls) -> Optional["ExceptionState"]:
        exc_type, value, tb = sys.exc_info()
        if exc_type and value and tb:
            return cls(exc_type=exc_type, value=value, tb=tb)

        return None

    def print(self, file: TextIO = sys.stderr) -> None:
        traceback.print_exception(self.exc_type, self.value, self.tb, file=file)
