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

    idents = set()
    for match in rx_identifier.finditer(text):
        start = match.start()
        end = match.end()

        if start > 0 and end < len(text) - 1:
            pre = text[start - 1 : start]
            post = text[end : end + 1]

            # we've matched a quoted ident - it's a string so don't include it
            if pre == post and pre in ('"', "'"):
                continue

        idents.add(match.group())

    return idents - set(get_func_names())
