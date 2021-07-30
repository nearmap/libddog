from typing import Any, Dict


JsonDict = Dict[str, Any]

def dict_matcher(dct: JsonDict, **kwargs: str) -> JsonDict:
    """
    Modifies the input `dct` by applying keys/values in `kwargs`.
    Used when the contents of `dct` are non-deterministic.
    """

    for key, value in kwargs.items():
        dct[key] = value

    return dct
