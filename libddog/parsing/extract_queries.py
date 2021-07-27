import pprint
from typing import Any, Dict, Iterator


class QueriedDoc:
    def __init__(self, *, id: str, title: str) -> None:
        self.id = id
        self.title = title


class QueryFound:
    def __init__(self, *, doc: QueriedDoc, id: str, title: str, query: str) -> None:
        self.doc = doc
        self.id = id
        self.title = title
        self.query = query


def get_queries(doc: Dict[Any, Any]) -> Iterator[QueryFound]:
    """Accepts a doc dict representing a dashboard and returns all the query
    strings found in it."""

    id = doc["id"]
    title = doc["title"]

    qdoc = QueriedDoc(id=id, title=title)

    def parse_widget(widget: Dict[Any, Any]) -> Iterator[QueryFound]:
        widget_id = widget["id"]
        defn = widget["definition"]
        widget_title = defn.get("title")
        requests = defn.get("requests", [])
        widget_type = defn["type"]
        widgets_nested = defn.get("widgets", [])  # widgets can be nested :/

        for widget in widgets_nested:
            yield from parse_widget(widget)

        # if it's an event widget or something - skip it
        omit_types = ("note", "event_stream", "event_timeline")
        if widget_type in omit_types:
            print("Skipping widget type: %s" % widget_type)
            return

        # sometimes 'requests' is just an object :/
        if not type(requests) == list:
            requests = [requests]

        for req in requests:
            query = req.get("q")
            if query:
                yield QueryFound(
                    doc=qdoc, id=widget_id, title=widget_title, query=query
                )

            # sometimes the query is inside a 'fill' object
            fill = req.get("fill")
            if fill:
                query = fill.get("q")
                if query:
                    yield QueryFound(
                        doc=qdoc, id=widget_id, title=widget_title, query=query
                    )

    for widget in doc["widgets"]:
        try:
            yield from parse_widget(widget)
        except Exception:
            print("Failed to parse widget:")
            pprint.pprint(widget)
            raise
