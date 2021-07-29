import enum
from typing import Any, Dict

from libddog.dashboards.enums import BackgroundColor, TextAlign, TickEdge, VerticalAlign


class NotePreset(enum.Enum):
    DEFAULT = 1
    CAPTION = 2
    HEADER = 3
    ANNOTATION = 4

    @classmethod
    def get_defaults(cls) -> Dict[Any, Any]:
        return {
            cls.DEFAULT: {
                "background_color": BackgroundColor.WHITE,
                "font_size": 14,
                "has_padding": True,
                "show_tick": False,
                "text_align": TextAlign.LEFT,
                "tick_edge": TickEdge.TOP,
                "vertical_align": VerticalAlign.TOP,
            },
            cls.CAPTION: {
                "background_color": BackgroundColor.TRANSPARENT,
                "font_size": 12,
                "has_padding": False,
                "show_tick": False,
                "text_align": TextAlign.LEFT,
                "tick_edge": TickEdge.LEFT,
                "vertical_align": VerticalAlign.TOP,
            },
            cls.HEADER: {
                "background_color": BackgroundColor.WHITE,
                "font_size": 36,
                "has_padding": True,
                "show_tick": False,
                "text_align": TextAlign.CENTER,
                "tick_edge": TickEdge.LEFT,
                "vertical_align": VerticalAlign.CENTER,
            },
            cls.ANNOTATION: {
                "background_color": BackgroundColor.YELLOW,
                "font_size": 14,
                "has_padding": True,
                "show_tick": True,
                "text_align": TextAlign.LEFT,
                "tick_edge": TickEdge.LEFT,
                "vertical_align": VerticalAlign.CENTER,
            },
        }
