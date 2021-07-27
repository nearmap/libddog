import re
from typing import Set

rx_identifier = re.compile("[a-zA-Z_][a-zA-Z_0-9]+")


def parse_formula_identifiers(text: str) -> Set[str]:
    """
    "100 * (q_4xx / q_all)" -> {"q_4xx", "q_all"}
    """
    return set(rx_identifier.findall(text))
