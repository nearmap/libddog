import enum
from typing import Any, Optional, Tuple

from libddog.metrics.bases import FormulaNode
from libddog.metrics.exceptions import FormulaValidationError
from libddog.metrics.literals import Float, Int
from libddog.metrics.query import By


class Function(FormulaNode):
    def __init__(self, *args: FormulaNode) -> None:
        self.args = args

    def codegen(self) -> str:
        name = self.__class__.__name__
        args = [arg.codegen() for arg in self.args]
        args_str = ", ".join(args)
        return "%s(%s)" % (name, args_str)


class FunctionWithSingleNode(Function):
    def __init__(self, node: FormulaNode) -> None:
        self.node = node

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()})"


# arithmetic


class abs(FunctionWithSingleNode):
    pass


class log2(FunctionWithSingleNode):
    pass


class log10(FunctionWithSingleNode):
    pass


class cumsum(FunctionWithSingleNode):
    pass


class integral(FunctionWithSingleNode):
    pass


# interpolation
# fill() is a FormulaNodeFunc so not mentioned here


class default_zero(FunctionWithSingleNode):
    pass


# timeshift


class hour_before(FunctionWithSingleNode):
    pass


class day_before(FunctionWithSingleNode):
    pass


class week_before(FunctionWithSingleNode):
    pass


class month_before(FunctionWithSingleNode):
    pass


class timeshift(Function):
    def __init__(self, node: FormulaNode, time_s: int) -> None:
        if time_s >= 0:
            raise FormulaValidationError(
                "timeshift interval must be below zero: %r" % time_s
            )

        self.node = node
        self.time_s = time_s

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, {self.time_s})"


# rate


class per_second(FunctionWithSingleNode):
    pass


class per_minute(FunctionWithSingleNode):
    pass


class per_hour(FunctionWithSingleNode):
    pass


class dt(FunctionWithSingleNode):
    pass


class diff(FunctionWithSingleNode):
    pass


class monotonic_diff(FunctionWithSingleNode):
    pass


class derivative(FunctionWithSingleNode):
    pass


# smoothing


class autosmooth(FunctionWithSingleNode):
    pass


class ewma_3(FunctionWithSingleNode):
    pass


class ewma_5(FunctionWithSingleNode):
    pass


class ewma_10(FunctionWithSingleNode):
    pass


class ewma_20(FunctionWithSingleNode):
    pass


class median_3(FunctionWithSingleNode):
    pass


class median_5(FunctionWithSingleNode):
    pass


class median_7(FunctionWithSingleNode):
    pass


class median_9(FunctionWithSingleNode):
    pass


# rollup
# remaining rollup use cases are handled as Rollup


class MovingRollupFunc(FormulaNode, enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"

    def codegen(self) -> str:
        return self.value


class moving_rollup(Function):
    def __init__(
        self, node: FormulaNode, interval_s: int, func: MovingRollupFunc
    ) -> None:
        self.args = (node, Int(interval_s), func)


# rank


class TopLimitTo(FormulaNode, enum.Enum):
    FIVE = 5
    TEN = 10
    TWENTY_FIVE = 25
    FIFTY = 50
    HUNDRED = 100

    def codegen(self) -> str:
        return f"{self.value}"


class TopBy(FormulaNode, enum.Enum):
    MAX = "max"
    MEAN = "mean"
    MIN = "min"
    SUM = "sum"
    LAST = "last"
    L2NORM = "l2norm"
    AREA = "area"

    def codegen(self) -> str:
        return f"'{self.value}'"


class TopDir(FormulaNode, enum.Enum):
    ASC = "asc"
    DESC = "desc"

    def codegen(self) -> str:
        return f"'{self.value}'"


class top(Function):
    def __init__(
        self, node: FormulaNode, limit_to: TopLimitTo, by: TopBy, dir: TopDir
    ) -> None:
        self.args = (node, limit_to, by, dir)


# TODO: variants of top / bottom


# count


class count_nonzero(FunctionWithSingleNode):
    pass


class count_not_null(FunctionWithSingleNode):
    pass


# regression


class robust_trend(FunctionWithSingleNode):
    pass


class trend_line(FunctionWithSingleNode):
    pass


class piecewise_constant(FunctionWithSingleNode):
    pass


# algorithms


class OutliersAlgo(FormulaNode, enum.Enum):
    DBSCAN = "DBSCAN"
    MAD = "MAD"
    SCALED_DBSCAN = "scaledDBSCAN"
    SCALED_MAD = "scaledMAD"

    def codegen(self) -> str:
        return f"'{self.value}'"


class outliers(Function):
    def __init__(
        self,
        node: FormulaNode,
        algo: OutliersAlgo,
        tolerance: float,
        pct: Optional[int] = None,
    ) -> None:
        args: Tuple[Any, ...] = (node, algo, Float(tolerance))

        if pct is not None:
            assert algo in (OutliersAlgo.MAD, OutliersAlgo.SCALED_MAD)
            args = (node, algo, Float(tolerance), Int(pct))

        self.args = args


class AnomaliesAlgo(FormulaNode, enum.Enum):
    BASIC = "basic"
    AGILE = "agile"
    ROBUST = "robust"

    def codegen(self) -> str:
        return f"'{self.value}'"


class anomalies(Function):
    def __init__(self, node: FormulaNode, algo: AnomaliesAlgo, bounds: int = 2) -> None:
        self.args = (node, algo, Int(bounds))


class ForecastAlgo(FormulaNode, enum.Enum):
    LINEAR = "linear"
    SEASONAL = "seasonal"


class forecast(Function):
    def __init__(self, node: FormulaNode, algo: ForecastAlgo, deviations: int) -> None:
        self.args = (node, algo, Int(deviations))


# exclusion


class exclude_null(Function):
    def __init__(self, node: FormulaNode, by: By) -> None:
        self.args = (node, by)


class cutoff_max(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.args = (node, Int(threshold))


class cutoff_min(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.args = (node, Int(threshold))


class clamp_max(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.args = (node, Int(threshold))


class clamp_min(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.args = (node, Int(threshold))
