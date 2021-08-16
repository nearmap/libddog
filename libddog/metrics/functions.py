import enum
from typing import Any, Optional, Tuple

from libddog.metrics.bases import FormulaNode
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


class FunctionWithSingleFormulaNode(Function):
    def __init__(self, node: FormulaNode) -> None:
        self.args = (node,)


# arithmetic


class abs(FunctionWithSingleFormulaNode):
    pass


class log2(FunctionWithSingleFormulaNode):
    pass


class log10(FunctionWithSingleFormulaNode):
    pass


class cumsum(FunctionWithSingleFormulaNode):
    pass


class integral(FunctionWithSingleFormulaNode):
    pass


# interpolation
# fill() is a FormulaNodeFunc so not mentioned here


class default_zero(FunctionWithSingleFormulaNode):
    pass


# timeshift


class hour_before(FunctionWithSingleFormulaNode):
    pass


class day_before(FunctionWithSingleFormulaNode):
    pass


class week_before(FunctionWithSingleFormulaNode):
    pass


class month_before(FunctionWithSingleFormulaNode):
    pass


class timeshift(Function):
    def __init__(self, node: FormulaNode, time_s: int) -> None:
        assert time_s < 0
        self.args = (node, Int(time_s))


# rate


class per_second(FunctionWithSingleFormulaNode):
    pass


class per_minute(FunctionWithSingleFormulaNode):
    pass


class per_hour(FunctionWithSingleFormulaNode):
    pass


class dt(FunctionWithSingleFormulaNode):
    pass


class diff(FunctionWithSingleFormulaNode):
    pass


class monotonic_diff(FunctionWithSingleFormulaNode):
    pass


class derivative(FunctionWithSingleFormulaNode):
    pass


# smoothing


class autosmooth(FunctionWithSingleFormulaNode):
    pass


class ewma_3(FunctionWithSingleFormulaNode):
    pass


class ewma_5(FunctionWithSingleFormulaNode):
    pass


class ewma_10(FunctionWithSingleFormulaNode):
    pass


class ewma_20(FunctionWithSingleFormulaNode):
    pass


class median_3(FunctionWithSingleFormulaNode):
    pass


class median_5(FunctionWithSingleFormulaNode):
    pass


class median_7(FunctionWithSingleFormulaNode):
    pass


class median_9(FunctionWithSingleFormulaNode):
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


class count_nonzero(FunctionWithSingleFormulaNode):
    pass


class count_not_null(FunctionWithSingleFormulaNode):
    pass


# regression


class robust_trend(FunctionWithSingleFormulaNode):
    pass


class trend_line(FunctionWithSingleFormulaNode):
    pass


class piecewise_constant(FunctionWithSingleFormulaNode):
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
