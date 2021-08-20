from libddog.metrics import Add, Div, Int, abs, timeshift
from libddog.metrics.query import FilterOperator
from libddog.parsing.query_parser import QueryParser

# def test_ast_builder__minimal_query() -> None:
#     parser = QueryParser()

#     qs = "avg:aws.ec2.cpuutilization"

#     ast = parser.parse_ast(qs)
#     expected = QueryState(
#         metric=Metric(name="aws.ec2.cpuutilization"),
#         agg=Aggregation(func=AggFunc.AVG),
#     )

#     assert ast.codegen() == expected.codegen()


# def test_ast_builder__exhaustive_query() -> None:
#     parser = QueryParser()

#     qs = (
#         "avg:aws.ec2.cpuutilization{$az, !role:cache} "
#         "by {az, role}.as_count().rollup(max, 110).fill(last, 112)"
#     )

#     ast = parser.parse_ast(qs)
#     expected = QueryState(
#         metric=Metric(name="aws.ec2.cpuutilization"),
#         filter=Filter(
#             conds=[
#                 TmplVar(tvar="az"),
#                 Tag(tag="role", value="cache", operator=FilterOperator.NOT_EQUAL),
#             ]
#         ),
#         agg=Aggregation(func=AggFunc.AVG, by=By(tags=["az", "role"]), as_=As.COUNT),
#         funcs=[
#             Rollup(func=RollupFunc.MAX, period_s=110),
#             Fill(func=FillFunc.LAST, limit_s=112),
#         ],
#     )

#     assert ast.codegen() == expected.codegen()


# def test_ast_builder__formula() -> None:
#     parser = QueryParser()

#     qs = "(abs(avg:aws.ec2.cpu) + 10) / timeshift(sum:aws.ec2.mem, -123)"

#     ast = parser.parse_ast(qs)
#     cpu = Query(
#         metric=Metric(name="aws.ec2.cpu"),
#         agg=Aggregation(func=AggFunc.AVG),
#     )
#     mem = Query(
#         metric=Metric(name="aws.ec2.mem"),
#         agg=Aggregation(func=AggFunc.SUM),
#     )
#     expected = Div(Add(abs(cpu), Int(10)), timeshift(mem, -123))

#     assert ast.codegen() == expected.codegen()
