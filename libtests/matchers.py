import re
from typing import Any, Dict, List

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


class PatchInstructionDidNotMatchAnything(Exception):
    pass


class PatchInstruction:
    def __init__(self, path: str) -> None:
        self.path = path
        self.times_applied = 0

    def count_application(self) -> None:
        self.times_applied += 1


class assign(PatchInstruction):
    def __init__(self, path: str, value: Any) -> None:
        super().__init__(path)
        self.value = value


rx_brackets_every = re.compile("\\[\\]")
rx_brackets_key = re.compile('\\["([a-z-A-Z0-9_-]+)"\\]')
rx_brackets_index = re.compile("\\[(-?[0-9]+)\\]")


def rewrite(obj: Any, path: str, instruction: PatchInstruction) -> Any:
    if not path:
        instruction.count_application()
        if isinstance(instruction, assign):
            return instruction.value

    # list index can be:
    # * positive: 1, 2, ...
    # * negative: -1, -2, ...
    match = rx_brackets_index.match(path)
    if match:
        # import pdb; pdb.set_trace()
        substr = match.group(0)
        idx = int(match.group(1))

        if not isinstance(obj, list):
            raise RuntimeError("Matched brackets index but obj is not a list: %r", obj)

        path_rest = path[len(substr) :]
        obj[idx] = rewrite(obj[idx], path_rest, instruction)
        return obj

    # dict key can only be a concrete key
    match = rx_brackets_key.match(path)
    if match:
        substr = match.group(0)
        key = match.group(1)

        if not isinstance(obj, dict):
            raise RuntimeError("Matched brackets index but obj is not a dict: %r", obj)

        path_rest = path[len(substr) :]
        obj[key] = rewrite(obj.get(key), path_rest, instruction)
        return obj

    # list or dict empty brackets means:
    # * apply to every item in list
    # * apply to every item in dict
    match = rx_brackets_every.match(path)
    if match:
        substr = match.group(0)
        path_rest = path[len(substr) :]

        if isinstance(obj, list):
            for idx, _ in enumerate(obj):
                obj[idx] = rewrite(obj[idx], path_rest, instruction)

        elif isinstance(obj, dict):
            for key in obj.keys():
                obj[key] = rewrite(obj[key], path_rest, instruction)

        return obj

    return obj


def obj_matcher(obj: Any, instructions: List[PatchInstruction]) -> Any:
    for instruction in instructions:
        path = instruction.path
        if path.startswith("."):
            path = path[1:]

        obj = rewrite(obj, path, instruction)

        if not instruction.times_applied:
            raise PatchInstructionDidNotMatchAnything(instruction.path)

    return obj
