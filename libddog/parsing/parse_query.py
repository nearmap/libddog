import re
from typing import Any, Dict, Iterator

agg_funcs = [
    "avg",
    "min",
    "max",
    "sum",
]

rx_query = re.compile(
    # fmt: off
    "(?P<agg>" + "|".join(agg_funcs) + ")" +  # aggregation
    ":" +
    "(?P<metric>.*?)" +  # metric name
    "\{(?P<filters>.*?)\}" +  # {...} filters
    "(?:" +
        "\s+by\s+\{(?P<by>.*?)\}" +  # by {...}
    ")?" +
    "(?:" +
        "\.(?P<as>as_.*?)\(\)" +  # .as_count() | as.rate()
    ")?" +
    "(?:" +
        "\.rollup\((?P<rollup>.*?)\)" +  # .rollup(<rollup_agg_func>, interval)
    ")?"
    # fmt: on
)


def parse_query(query: str) -> Iterator[Dict[Any, Any]]:
    for match in rx_query.finditer(query):
        yield match.groupdict()
