from typing import List

from libddog.metrics.bases import FormulaNode
from libddog.metrics.literals import Identifier


def find_identifiers(node: FormulaNode) -> List[Identifier]:
    if isinstance(node, Identifier):
        return [node]

    children = []
    for attname in dir(node):
        value = getattr(node, attname)
        if not isinstance(value, FormulaNode):
            continue
        children.append(value)

    identifiers = []
    for child in children:
        idents = find_identifiers(child)
        identifiers.extend(idents)

    return identifiers
