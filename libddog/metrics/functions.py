import enum
from typing import Any, Optional, Tuple

from libddog.metrics.bases import QueryNode
from libddog.metrics.literals import Float, Int
from libddog.metrics.query import By, Query


class Function(QueryNode):
    def __init__(self, *args: QueryNode) -> None:
        self.args = args

    def codegen(self) -> str:
        name = self.__class__.__name__
        args = [arg.codegen() for arg in self.args]
        args_str = ", ".join(args)
        return "%s(%s)" % (name, args_str)


class FunctionWithSingleQuery(Function):
    def __init__(self, expr: Query) -> None:
        self.args = (expr,)


# arithmetic


class abs(FunctionWithSingleQuery):
    pass


class log2(FunctionWithSingleQuery):
    pass


class log10(FunctionWithSingleQuery):
    pass


class cumsum(FunctionWithSingleQuery):
    pass


class integral(FunctionWithSingleQuery):
    pass


# interpolation
# fill() is a QueryFunc so not mentioned here


class default_zero(FunctionWithSingleQuery):
    def __init__(self, expr: Query) -> None:
        self.args = (expr,)


# timeshift


class hour_before(FunctionWithSingleQuery):
    pass


class day_before(FunctionWithSingleQuery):
    pass


class week_before(FunctionWithSingleQuery):
    pass


class month_before(FunctionWithSingleQuery):
    pass


class timeshift(Function):
    def __init__(self, expr: Query, time_s: int) -> None:
        assert time_s < 0
        self.args = (expr, Int(time_s))


# rate


class per_second(FunctionWithSingleQuery):
    pass


class per_minute(FunctionWithSingleQuery):
    pass


class per_hour(FunctionWithSingleQuery):
    pass


class dt(FunctionWithSingleQuery):
    pass


class diff(FunctionWithSingleQuery):
    pass


class monotonic_diff(FunctionWithSingleQuery):
    pass


class derivative(FunctionWithSingleQuery):
    pass


# smoothing


class autosmooth(FunctionWithSingleQuery):
    pass


class ewma_3(FunctionWithSingleQuery):
    pass


class ewma_5(FunctionWithSingleQuery):
    pass


class ewma_10(FunctionWithSingleQuery):
    pass


class ewma_20(FunctionWithSingleQuery):
    pass


class median_3(FunctionWithSingleQuery):
    pass


class median_5(FunctionWithSingleQuery):
    pass


class median_7(FunctionWithSingleQuery):
    pass


class median_9(FunctionWithSingleQuery):
    pass


# rollup
# remaining rollup use cases are handled as Rollup


class MovingRollupFunc(QueryNode, enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"

    def codegen(self) -> str:
        return self.value


class moving_rollup(Function):
    def __init__(self, expr: Query, interval_s: int, func: MovingRollupFunc) -> None:
        self.args = (expr, Int(interval_s), func)


# rank


class TopLimitTo(QueryNode, enum.Enum):
    FIVE = 5
    TEN = 10
    TWENTY_FIVE = 25
    FIFTY = 50
    HUNDRED = 100

    def codegen(self) -> str:
        return f"{self.value}"


class TopBy(QueryNode, enum.Enum):
    MAX = "max"
    MEAN = "mean"
    MIN = "min"
    SUM = "sum"
    LAST = "last"
    L2NORM = "l2norm"
    AREA = "area"

    def codegen(self) -> str:
        return f"'{self.value}'"


class TopDir(QueryNode, enum.Enum):
    ASC = "asc"
    DESC = "desc"

    def codegen(self) -> str:
        return f"'{self.value}'"


class top(Function):
    def __init__(
        self, expr: Query, limit_to: TopLimitTo, by: TopBy, dir: TopDir
    ) -> None:
        self.args = (expr, limit_to, by, dir)


# TODO: variants of top / bottom


# count


class count_nonzero(FunctionWithSingleQuery):
    pass


class count_not_null(FunctionWithSingleQuery):
    pass


# regression


class robust_trend(FunctionWithSingleQuery):
    pass


class trend_line(FunctionWithSingleQuery):
    pass


class piecewise_constant(FunctionWithSingleQuery):
    pass


# algorithms


class OutliersAlgo(QueryNode, enum.Enum):
    # TODO: values
    DBSCAN = "dbscan"
    MAD = "mad"
    SCALED_DBSCAN = "dbscan"
    SCALED_MAD = "dbscan"

    def codegen(self) -> str:
        return f"'{self.value}'"


class outliers(Function):
    def __init__(
        self,
        expr: Query,
        algo: OutliersAlgo,
        tolerance: float,
        pct: Optional[int] = None,
    ) -> None:
        args: Tuple[Any, ...] = (expr, algo, Float(tolerance))

        if pct is not None:
            assert algo in (OutliersAlgo.MAD, OutliersAlgo.SCALED_MAD)
            args = (expr, algo, Float(tolerance), Int(pct))

        self.args = args


class AnomaliesAlgo(QueryNode, enum.Enum):
    BASIC = "basic"
    AGILE = "agile"
    ROBUST = "robust"

    def codegen(self) -> str:
        return f"'{self.value}'"


class anomalies(Function):
    def __init__(self, expr: Query, algo: AnomaliesAlgo, bounds: int = 2) -> None:
        self.args = (expr, algo, Int(bounds))


class ForecastAlgo(QueryNode, enum.Enum):
    LINEAR = "linear"
    SEASONAL = "seasonal"


class forecast(Function):
    def __init__(self, expr: Query, algo: ForecastAlgo, deviations: int) -> None:
        self.args = (expr, algo, Int(deviations))


# exclusion


class exclude_null(Function):
    def __init__(self, expr: Query, by: By) -> None:
        self.args = (expr, by)


class cutoff_max(Function):
    def __init__(self, expr: Query, threshold: int) -> None:
        self.args = (expr, Int(threshold))


class cutoff_min(Function):
    def __init__(self, expr: Query, threshold: int) -> None:
        self.args = (expr, Int(threshold))


class clamp_max(Function):
    def __init__(self, expr: Query, threshold: int) -> None:
        self.args = (expr, Int(threshold))


class clamp_min(Function):
    def __init__(self, expr: Query, threshold: int) -> None:
        self.args = (expr, Int(threshold))
