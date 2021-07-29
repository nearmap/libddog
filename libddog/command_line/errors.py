import sys
import traceback
from typing import Optional


class ExceptionState:
    def __init__(self, type, value, tb) -> None:
        self.type = type
        self.value = value
        self.tb = tb

    @classmethod
    def create(cls) -> Optional["ExceptionState"]:
        type, value, tb = sys.exc_info()
        if type and value and tb:
            return cls(type=type, value=value, tb=tb)

        return None

    def print(self, file=sys.stderr):
        traceback.print_exception(self.type, self.value, self.tb, file=file)
