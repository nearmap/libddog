from typing import Any, Dict, List, Optional, Sequence

from libddog.common.types import JsonDict
from libddog.dashboards.components import (
    Layout,
    Marker,
    Position,
    Request,
    Size,
    Time,
    YAxis,
)
from libddog.dashboards.enums import (
    BackgroundColor,
    LayoutType,
    LegendColumn,
    LegendLayout,
    LiveSpan,
    ResponseFormat,
    TextAlign,
    TickEdge,
    TitleAlign,
    VerticalAlign,
)
from libddog.dashboards.presets import NotePreset
from libddog.metrics.query import QueryState


class Widget:
    _allowed_atts: Dict[Any, Sequence[str]] = {}

    """
    A visual component on a dashboard.
    """

    def as_dict(self) -> JsonDict:
        raise NotImplementedError

    def add_layout(self, dct: JsonDict, size: Size, position: Position) -> None:
        """
        Transforms:

            {
                "definition": {...},
            }

        ...into:

            {
                "definition": {...},
                "layout": {...},
            }
        """

        layout = Layout(size=size, position=position)
        dct_layout = layout.as_dict()
        dct.update(dct_layout)

    def _get_allowed_atts(self, obj: Any) -> Sequence[str]:
        cls = obj.__class__
        allowed_atts = self._allowed_atts.get(cls)
        if allowed_atts is None:
            raise NotImplementedError("allowed atts for: %r" % cls)

        # sanity check: make sure present default attributes do exist
        for attname in allowed_atts:
            if not hasattr(obj, attname):
                raise RuntimeError(
                    "Invalid att name in allowed_atts for %s: %s" % (cls, attname)
                )

        return allowed_atts

    def _filter_dict_keys(
        self, dct: Dict[str, Any], allowed_atts: Sequence[str]
    ) -> None:
        for key in list(dct.keys()):
            if key not in allowed_atts:
                del dct[key]

    def query_as_dict(self, query: QueryState) -> JsonDict:
        dct = query.as_dict()
        allowed_atts = self._get_allowed_atts(query)
        self._filter_dict_keys(dct, allowed_atts)
        return dct

    def request_as_dict(self, request: Request) -> JsonDict:
        dct = request.as_dict()
        allowed_atts = self._get_allowed_atts(request)
        self._filter_dict_keys(dct, allowed_atts)

        # overwrite 'queries' using our custom implementation
        dct["queries"] = [self.query_as_dict(query._state) for query in request.queries]

        return dct


class Note(Widget):
    def __init__(
        self,
        *,
        preset: NotePreset = NotePreset.DEFAULT,
        content: str,
        background_color: Optional[BackgroundColor] = None,
        font_size: Optional[int] = None,
        text_align: Optional[TextAlign] = None,
        vertical_align: Optional[VerticalAlign] = None,
        show_tick: Optional[bool] = None,
        tick_edge: Optional[TickEdge] = None,
        has_padding: Optional[bool] = None,
        size: Optional[Size] = None,
        position: Optional[Position] = None,
    ) -> None:
        self.preset = preset
        self.content = content
        self.background_color = background_color
        self.font_size = font_size
        self.text_align = text_align
        self.vertical_align = vertical_align
        self.show_tick = show_tick
        self.tick_edge = tick_edge
        self.has_padding = has_padding
        self.size = Size.backfill(self, size)
        self.position = position or Position()

    def apply_preset(self) -> "Note":
        """
        Create a new Note instance where the present default values have been
        applied for any optional attributes which are not set on 'self'.
        """

        preset_defaults = NotePreset.get_defaults().get(self.preset)
        if not preset_defaults:
            raise NotImplementedError(self.preset)

        # sanity check: make sure present default attributes do exist
        for attname in preset_defaults.keys():
            if not hasattr(self, attname):
                raise RuntimeError("Invalid att name in preset: %s" % attname)

        # the effective values of the attributes
        kwargs = {}

        # get all the attribute names on 'self'
        attnames = [
            att
            for att in dir(self)
            if not att.startswith("_") and not callable(getattr(self, att))
        ]

        for attname in attnames:
            value = getattr(self, attname, None)

            # if the attribute is not set on 'self' get it from the preset
            # defaults instead
            if value is None:
                value = preset_defaults.get(attname)

                # if it's present in the present it must be set
                assert value is not None

            kwargs[attname] = value

        return self.__class__(**kwargs)

    def as_dict(self) -> JsonDict:
        instance = self.apply_preset()
        # from this point on: use 'instance' not 'self'

        # let's help mypy a bit because these are no longer None
        assert instance.background_color is not None
        assert instance.text_align is not None
        assert instance.tick_edge is not None
        assert instance.vertical_align is not None

        dct = {
            "definition": {
                "background_color": instance.background_color.value,
                "content": instance.content,
                "font_size": str(instance.font_size),
                "has_padding": instance.has_padding,
                "show_tick": instance.show_tick,
                "text_align": instance.text_align.value,
                "tick_edge": instance.tick_edge.value,
                "type": "note",
                "vertical_align": instance.vertical_align.value,
            },
        }

        instance.add_layout(dct, size=instance.size, position=instance.position)
        return dct


class QueryValue(Widget):
    _allowed_atts = {
        QueryState: [
            "aggregator",
            "data_source",
            "name",
            "query",
        ],
        Request: [
            "formulas",
            "conditional_formats",
            "queries",
        ],
    }

    def __init__(
        self,
        *,
        title: str,
        title_size: int = 16,
        title_align: TitleAlign = TitleAlign.LEFT,
        time: Optional[Time] = None,
        autoscale: bool = True,
        custom_unit: Optional[str] = None,
        precision: int = 2,
        requests: List[Request],
        size: Optional[Size] = None,
        position: Optional[Position] = None,
    ) -> None:
        self.title = title
        self.title_size = title_size
        self.title_align = title_align
        self.time = time or Time(live_span=LiveSpan.GLOBAL_TIME)
        self.autoscale = autoscale
        self.custom_unit = custom_unit
        self.precision = precision
        self.requests = requests
        self.size = Size.backfill(self, size)
        self.position = position or Position()

    def request_as_dict(self, request: Request) -> Dict[str, Any]:
        dct = super().request_as_dict(request)
        dct["response_format"] = ResponseFormat.SCALAR.value
        return dct

    def as_dict(self) -> JsonDict:
        dct = {
            "definition": {
                "autoscale": self.autoscale,
                "precision": self.precision,
                "requests": [self.request_as_dict(req) for req in self.requests],
                "time": self.time.as_dict(),
                "title": self.title,
                "title_align": self.title_align.value,
                "title_size": str(self.title_size),
                "type": "query_value",
            },
        }

        if self.custom_unit:
            dct["definition"]["custom_unit"] = self.custom_unit

        self.add_layout(dct, size=self.size, position=self.position)
        return dct


class Timeseries(Widget):
    _allowed_atts = {
        QueryState: [
            "data_source",
            "name",
            "query",
        ],
        Request: [
            "display_type",
            "formulas",
            "on_right_yaxis",
            "queries",
            "style",
            "title",
        ],
    }

    def __init__(
        self,
        *,
        title: str,
        title_size: int = 16,
        title_align: TitleAlign = TitleAlign.LEFT,
        show_legend: bool = True,
        legend_layout: LegendLayout = LegendLayout.AUTOMATIC,
        legend_columns: Optional[Sequence[LegendColumn]] = None,
        requests: List[Request],
        yaxis: Optional[YAxis] = None,
        markers: Optional[Sequence[Marker]] = None,
        size: Optional[Size] = None,
        position: Optional[Position] = None,
    ) -> None:
        self.title = title
        self.title_size = title_size
        self.title_align = title_align
        self.show_legend = show_legend
        self.legend_layout = legend_layout
        self.legend_columns = legend_columns or [
            LegendColumn.AVG,
            LegendColumn.MIN,
            LegendColumn.MAX,
            LegendColumn.VALUE,
            LegendColumn.SUM,
        ]
        self.requests = requests
        self.yaxis = yaxis or YAxis()
        self.markers = markers or []
        self.size = Size.backfill(self, size)
        self.position = position or Position()

    def request_as_dict(self, request: Request) -> JsonDict:
        dct = super().request_as_dict(request)
        dct["response_format"] = ResponseFormat.TIMESERIES.value
        return dct

    def as_dict(self) -> JsonDict:
        dct = {
            "definition": {
                "legend_columns": [col.value for col in self.legend_columns],
                "legend_layout": self.legend_layout.value,
                "markers": [marker.as_dict() for marker in self.markers],
                "requests": [self.request_as_dict(req) for req in self.requests],
                "show_legend": self.show_legend,
                "title": self.title,
                "title_align": self.title_align.value,
                "title_size": str(self.title_size),
                "type": "timeseries",
                "yaxis": self.yaxis.as_dict(),
            },
        }

        self.add_layout(dct, size=self.size, position=self.position)
        return dct


class Group(Widget):
    """A visual container with a title that contains widgets."""

    def __init__(
        self,
        *,
        title: str,
        layout_type: LayoutType = LayoutType.ORDERED,
        background_color: Optional[BackgroundColor] = None,
        widgets: Optional[Sequence[Widget]] = None,
        size: Optional[Size] = None,
        position: Optional[Position] = None,
    ) -> None:
        self.title = title
        self.layout_type = layout_type
        self.background_color = background_color
        self.widgets = widgets or []
        self.size = Size.backfill(self, size)
        self.position = position or Position()

    def as_dict(self) -> JsonDict:
        dct = {
            "definition": {
                "title": self.title,
                "type": "group",
                "layout_type": self.layout_type.value,
                "widgets": [wid.as_dict() for wid in self.widgets],
            },
        }

        if self.background_color:
            dct["definition"]["background_color"] = self.background_color.value

        self.add_layout(dct, size=self.size, position=self.position)
        return dct
