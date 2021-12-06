from typing import List

from libddog.dashboards.components import Position, Size
from libddog.dashboards.exceptions import HLayoutError
from libddog.dashboards.presets import NotePreset
from libddog.dashboards.widgets import Note, Widget


class HLayout:
    page_width = 12

    def __init__(self, width: int, height: int, widgets: List[Widget]) -> None:
        self.width = width
        self.height = height
        self.widgets = widgets

    def _lay_out_widgets(self) -> None:
        cum_width = 0
        y_pos = 0

        for widget in self.widgets:
            overflow = (cum_width + self.width) - self.page_width
            if overflow > 0:
                raise HLayoutError("Overflowed page width by %r units" % overflow)

            widget.size.width = self.width
            widget.size.height = self.height

            widget.position.x = cum_width
            widget.position.y = y_pos

            cum_width += widget.size.width

        delta_width = abs(self.page_width - cum_width)
        if delta_width > 0:
            note = Note(
                preset=NotePreset.CAPTION,
                content="",
                size=Size(width=delta_width, height=self.height),
                position=Position(x=cum_width, y=y_pos),
            )
            self.widgets.append(note)

    def get_widgets(self) -> List[Widget]:
        self._lay_out_widgets()
        return self.widgets


class HLayoutStack:
    def __init__(self, layouts: List[HLayout]) -> None:
        self.layouts = layouts

    def _lay_out_widgets(self) -> None:
        for layout in self.layouts:
            layout._lay_out_widgets()

        cum_height = 0
        for layout in self.layouts:
            for widget in layout.widgets:
                widget.position.y = cum_height

            cum_height += layout.height

    def get_widgets(self) -> List[Widget]:
        self._lay_out_widgets()

        widgets = []
        for layout in self.layouts:
            widgets.extend(layout.widgets)

        return widgets
