import re
from typing import List, Set

import libddog.metrics.functions
from libddog.metrics.functions import Function

rx_identifier = re.compile("[a-zA-Z_][a-zA-Z_0-9]+")


def get_func_names() -> List[str]:
    # TODO: will also include base classes which are not function names
    names = []
    mod = libddog.metrics.functions

    for attname in dir(mod):
        cls = getattr(mod, attname)
        try:
            if issubclass(cls, Function):
                names.append(cls.__name__)
        except TypeError:
            pass

    return names


def parse_formula_identifiers(text: str) -> Set[str]:
    """
    "100 * (q_4xx / q_all)" -> {"q_4xx", "q_all"}
    """
    idents = set(rx_identifier.findall(text))
    return idents - set(get_func_names())
