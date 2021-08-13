import enum
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


class PatchOp(enum.Enum):
    NOOP = 0
    SET = 1
    DELETE = 2


class PatchInstruction:
    def __init__(self, path: str, value: str, op: PatchOp) -> None:
        self.path = path
        self.value = value
        self.op = op

    def maybe_apply(self, path: str) -> Any:
        if self.path == path:
            if self.op is PatchOp.SET:
                return self.op, self.value
            elif self.op is PatchOp.DELETE:
                return self.op, None

        return PatchOp.NOOP, None


class ObjectPatcher:
    def __init__(self, instructions: List[PatchInstruction]) -> None:
        self.instructions = instructions

    @classmethod
    def create(cls, patches: Dict[str, Any]) -> "ObjectPatcher":
        instructions = []

        for key, value in patches.items():
            op_elem, _, path = key.partition(" ")

            op = None
            if op_elem == "-":
                op = PatchOp.DELETE
            elif op_elem == "=":
                op = PatchOp.SET
            else:
                raise ValueError("Unsupported op: %s" % op_elem)

            if not path.startswith("/"):
                raise ValueError("Invalid patch path: %s" % path)

            instruction = PatchInstruction(path=path, value=value, op=op)
            instructions.append(instruction)
            # print(instruction.__dict__)

        return cls(instructions=instructions)

    def apply_all_to_dict(self, path: str, dct: Dict[str, Any], key: str) -> None:
        for instruction in self.instructions:
            op, new_value = instruction.maybe_apply(path)
            if op is PatchOp.SET:
                dct[key] = new_value
            elif op is PatchOp.DELETE:
                del dct[key]

    def apply_all_to_list(self, path: str, lst: List[Any], idx: int) -> None:
        for instruction in self.instructions:
            op, new_value = instruction.maybe_apply(path)
            if op is PatchOp.SET:
                lst[idx] = new_value
            elif op is PatchOp.DELETE:
                del lst[idx]

    def rewrite(self, obj: object, path="/") -> Any:
        # import pdb; pdb.set_trace()
        if isinstance(obj, dict):
            orig_dict = obj
            cloned_dict = dict(obj)

            # can't modify the dict while iterating over it, so iterate over the
            # original and modify the clone
            for key in orig_dict.keys():
                nested_path = f"{path}{key}"
                self.apply_all_to_dict(nested_path, cloned_dict, key)

            return cloned_dict

        elif isinstance(obj, list):
            orig_list = obj
            cloned_list = list(obj)

            for i, _ in enumerate(orig_list):
                nested_path = f"{path}[{i}]"
                self.apply_all_to_list(nested_path, cloned_list, i)

            return cloned_list


def obj_matcher(dct: JsonDict, patches: Dict[Any, Any]) -> JsonDict:
    patcher = ObjectPatcher.create(patches)
    return patcher.rewrite(dct)
