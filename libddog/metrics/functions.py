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
    _valid_methods = frozenset(
        {
            "avg",
            "min",
            "max",
            "sum",
            "count",
        }
    )

    def __init__(self, node: FormulaNode, period_s: int, method: str) -> None:
        if method not in self._valid_methods:
            alternatives = ", ".join(
                [f"{alt!r}" for alt in sorted(self._valid_methods)]
            )
            raise FormulaValidationError(
                "moving_rollup method %r must be one of: %s" % (method, alternatives)
            )

        self.node = node
        self.period_s = period_s
        self.method = method

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, {self.period_s}, '{self.method}')"


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


class outliers(Function):
    _valid_algorithms = frozenset(
        {
            "DBSCAN",
            "MAD",
            "scaledDBSCAN",
            "scaledMAD",
        }
    )
    _allow_pct_arg = frozenset(
        {
            "MAD",
            "scaledMAD",
        }
    )

    def __init__(
        self,
        node: FormulaNode,
        algorithm: str,
        tolerance: float,
        pct: Optional[int] = None,
    ) -> None:
        if algorithm not in self._valid_algorithms:
            alternatives = ", ".join(
                [f"{alt!r}" for alt in sorted(self._valid_algorithms)]
            )
            raise FormulaValidationError(
                "outliers algorithm %r must be one of: %s" % (algorithm, alternatives)
            )

        if pct is not None and algorithm not in self._allow_pct_arg:
            alternatives = ", ".join(
                [f"{alt!r}" for alt in sorted(self._allow_pct_arg)]
            )
            raise FormulaValidationError(
                "outliers pct only valid for algorithms: %s" % alternatives
            )

        self.node = node
        self.algorithm = algorithm
        self.tolerance = tolerance
        self.pct = pct

    def codegen(self) -> str:
        func_name = self.__class__.__name__

        args = [self.node.codegen(), f"'{self.algorithm}'", f"{self.tolerance}"]
        if self.pct is not None:
            args.append(f"{self.pct}")

        args_fmt = ", ".join(args)
        return f"{func_name}({args_fmt})"


class anomalies(Function):
    _valid_algorithms = frozenset({"basic", "agile", "robust"})

    def __init__(self, node: FormulaNode, algorithm: str, bounds: int = 2) -> None:
        if algorithm not in self._valid_algorithms:
            alternatives = ", ".join(
                [f"{alt!r}" for alt in sorted(self._valid_algorithms)]
            )
            raise FormulaValidationError(
                "anomalies algorithm %r must be one of: %s" % (algorithm, alternatives)
            )

        self.node = node
        self.algorithm = algorithm
        self.bounds = bounds

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, '{self.algorithm}', {self.bounds})"


class forecast(Function):
    _valid_algorithms = frozenset({"linear", "seasonal"})

    def __init__(self, node: FormulaNode, algorithm: str, deviations: int) -> None:
        if algorithm not in self._valid_algorithms:
            alternatives = ", ".join(
                [f"{alt!r}" for alt in sorted(self._valid_algorithms)]
            )
            raise FormulaValidationError(
                "forecast algorithm %r must be one of: %s" % (algorithm, alternatives)
            )

        self.node = node
        self.algorithm = algorithm
        self.deviations = deviations

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return (
            f"{func_name}({self.node.codegen()}, '{self.algorithm}', {self.deviations})"
        )


# exclusion


class exclude_null(Function):
    def __init__(self, node: FormulaNode, by: str) -> None:
        self.node = node
        self.by = by

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, '{self.by}')"


class cutoff_max(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.node = node
        self.threshold = threshold

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, {self.threshold})"


class cutoff_min(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.node = node
        self.threshold = threshold

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, {self.threshold})"


class clamp_max(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.node = node
        self.threshold = threshold

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, {self.threshold})"


class clamp_min(Function):
    def __init__(self, node: FormulaNode, threshold: int) -> None:
        self.node = node
        self.threshold = threshold

    def codegen(self) -> str:
        func_name = self.__class__.__name__
        return f"{func_name}({self.node.codegen()}, {self.threshold})"
