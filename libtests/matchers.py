from typing import Any, Dict

from libddog.common.types import JsonDict


def dict_matcher(dct: JsonDict, *args: Dict[Any, Any], **patches: str) -> JsonDict:
    """
    Modifies the input `dct` by applying keys/values in `patches`.
    Used when the contents of `dct` are non-deterministic.
    """

    if args:
        patches_as_optional_param = args[0]
        patches.update(patches_as_optional_param)

    for key, value in patches.items():
        dct[key] = value

    return dct


class DictComparator:
    def __init__(self) -> None:
        pass

    def cmp(self, expected: JsonDict, actual: JsonDict) -> None:
        pass
