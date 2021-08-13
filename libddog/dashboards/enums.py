import enum


class BackgroundColor(enum.Enum):
    BLUE = "blue"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    WHITE = "white"
    YELLOW = "yellow"
    VIVID_BLUE = "vivid_blue"
    VIVID_GREEN = "vivid_green"
    VIVID_ORANGE = "vivid_orange"
    VIVID_PINK = "vivid_pink"
    VIVID_PURPLE = "vivid_purple"
    VIVID_YELLOW = "vivid_yellow"
    NEUTRAL = "white"
    TRANSPARENT = "transparent"


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


class LegendColumn(enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    VALUE = "value"
    SUM = "sum"


class LegendLayout(enum.Enum):
    AUTOMATIC = "auto"
    COMPACT = "horizontal"
    EXPANDED = "vertical"


class LineType(enum.Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


class LineWidth(enum.Enum):
    NORMAL = "normal"
    THIN = "thin"
    THICK = "thick"


class LiveSpan(enum.Enum):
    GLOBAL_TIME = ""  # intentionally the empty string
    LAST_1M = "1m"
    LAST_5M = "5m"
    LAST_15M = "15m"
    LAST_1H = "1h"
    LAST_4H = "4h"
    LAST_1D = "1d"
    LAST_2D = "2d"
    LAST_1W = "1w"
    LAST_3MO = "3mo"
    LAST_6MO = "6mo"
    LAST_1Y = "1y"


class MarkerLineStyle(enum.Enum):
    SOLID = "solid"
    BOLD = "bold"
    DASHED = "dashed"


class MarkerSeverity(enum.Enum):
    ERROR = "error"
    WARNING = "warning"
    OK = "ok"
    INFO = "info"


class Palette(enum.Enum):
    CLASSIC = "dog_classic"
    COOL = "cool"
    WARM = "warm"
    PURPLE = "purple"
    ORANGE = "orange"
    # yes the typo is intentional lol. In the Datadog UI it's spelled gray, in
    # json it's spelled grey
    GRAY = "grey"


class ResponseFormat(enum.Enum):
    SCALAR = "scalar"
    TIMESERIES = "timeseries"
    # have not validated the other alternatives yet


class Scale(enum.Enum):
    LINEAR = "linear"
    LOG = "log"
    POW = "pow"
    SQRT = "sqrt"


class TextAlign(enum.Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TickEdge(enum.Enum):
    RIGHT = "right"
    LEFT = "left"
    BOTTOM = "bottom"
    TOP = "top"


class TitleAlign(enum.Enum):
    LEFT = "left"
    # 'center' and 'right' seem to have no effect
    # have not validated the other alternatives yet


class VerticalAlign(enum.Enum):
    BOTTOM = "bottom"
    CENTER = "center"
    TOP = "top"
