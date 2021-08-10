from libddog.metrics import AggFunc, Aggregation, Metric, Query
from libddog.parsing.query_parser import QueryParser


def test_ast_builder() -> None:
    parser = QueryParser()

    # qs = 'abs(avg:aws.ec2.cpuutilization)'
    qs = "avg:aws.ec2.cpuutilization"

    ast = parser.parse_ast(qs)

    assert ast.codegen() == Query(
        metric=Metric(name="aws.ec2.cpuutilization"),
        agg=Aggregation(func=AggFunc.AVG),
    ).codegen()
