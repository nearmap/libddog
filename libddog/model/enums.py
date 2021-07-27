import enum


class BackgroundColor(enum.Enum):
    YELLOW = "yellow"
    WHITE = "white"
    # have not validated the other alternatives yet


class Comparator(enum.Enum):
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="


class ConditionalFormatPalette(enum.Enum):
    WHITE_ON_GREEN = "white_on_green"
    WHITE_ON_RED = "white_on_red"
    WHITE_ON_YELLOW = "white_on_yellow"


class DisplayType(enum.Enum):
    LINES = "line"
    AREAS = "area"
    BARS = "bars"


class LayoutType(enum.Enum):
    ORDERED = "ordered"
    # have not validated the other alternatives yet


class LineType(enum.Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


class LineWidth(enum.Enum):
    NORMAL = "normal"
    THIN = "thin"
    THICK = "thick"


class Palette(enum.Enum):
    CLASSIC = "dog_classic"
    COOL = "cool"
    WARM = "warm"
    PURPLE = "purple"
    ORANGE = "orange"
    GRAY = "grey"  # yes the typo is intentional lol


class ResponseFormat(enum.Enum):
    SCALAR = "scalar"
    TIMESERIES = "timeseries"
    # have not validated the other alternatives yet


class Scale(enum.Enum):
    LINEAR = "linear"
    # have not validated the other alternatives yet


class TextAlign(enum.Enum):
    LEFT = "left"
    # have not validated the other alternatives yet


class TickEdge(enum.Enum):
    LEFT = "left"
    TOP = "top"
    # have not validated the other alternatives yet


class TitleAlign(enum.Enum):
    LEFT = "left"
    # have not validated the other alternatives yet


class VerticalAlign(enum.Enum):
    CENTER = "center"
    TOP = "top"
    # have not validated the other alternatives yet
