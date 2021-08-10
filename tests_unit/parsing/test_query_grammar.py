import sys

from parsimonious.exceptions import IncompleteParseError, ParseError

from libddog.parsing.query_parser import QueryParser


def test_grammar() -> None:
    single_query_cases = [
        ("minimal query", "avg:svcname"),
        ("suspect: no aggregation", "svcname"),
        # multipart name
        ("multipart metric name", "avg:svcname.s3"),
        ("subsequent part starts with digit", "avg:svcname.s3.95percentile"),
        ("suspect: part is empty string", "avg:svcname.s3."),
        # filter
        ("single tvar", "avg:svcname{$region}"),
        ("single tag", "avg:svcname{region:us-east-1}"),
        ("wildcard", "avg:svcname{*}"),
        ("tvars and tags", "avg:svcname{$region,box:blue,$db,name:bob}"),
        ("tag negation", "avg:svcname{!region:us-east-1}"),
        ("corner case: whitespace", "avg:svcname{  $region  ,   box:blue  }"),
        ("corner case: tag name charset #1", "avg:svcname{_reg-ion_:us-east-1}"),
        ("corner case: tag name charset #2", "avg:svcname{kubernetes.io/namespace:db}"),
        ("tag value wildcard prefix", "avg:svcname{region:*-east-1}"),
        ("tag value wildcard suffix", "avg:svcname{region:us-east-*}"),
        ("corner case: tag value charset #1", "avg:svcname{db:arn:aws:rds}"),
        ("corner case: tag value charset #2", "avg:svcname{path:/dev/null}"),
        ("corner case: tag value charset #3", "avg:svcname{func:users.create}"),
        ("suspect: tag without value", "avg:svcname{region}"),
        ("suspect: just dollar sign", "avg:svcname{$}"),
        # by
        ("single tag", "avg:svcname{*} by {db}"),
        ("tag and tvar", "avg:svcname{*} by {db,$region}"),
        ("corner case: whitespace", "avg:svcname{*}by{  db  ,   $region  }"),
        # as
        ("count", "avg:svcname{*}.as_count()"),
        ("rate", "avg:svcname{*}.as_rate()"),
        # rollup
        ("func only", "avg:svcname{*}.rollup(sum)"),
        ("func and period", "avg:svcname{*}.rollup(sum,13)"),
        ("corner case: whitespace", "avg:svcname{*}.rollup(  sum   ,  13   )"),
        # fill
        ("int value", "avg:svcname{*}.fill(0)"),
        ("func value", "avg:svcname{*}.fill(zero)"),
        ("func and limit", "avg:svcname{*}.fill(zero, 4)"),
        ("corner case: whitespace", "avg:svcname{*}.fill(  zero   ,  4   )"),
        # combinations of components
        ("all", "avg:svcname{db:toys} by {az}.as_rate().rollup(sum).fill(zero)"),
        ("no by", "avg:svcname{db:toys}.as_rate().rollup(sum).fill(zero)"),
        ("no as", "avg:svcname{db:toys} by {az}.rollup(sum).fill(zero)"),
        ("no rollup", "avg:svcname{db:toys} by {az}.as_rate().fill(zero)"),
        ("no fill", "avg:svcname{db:toys} by {az}.as_rate().rollup(sum)"),
        # permutations of rollup/fill
        ("fill first", "avg:svcname{db:toys}.fill(zero).rollup(sum)"),
    ]

    function_cases = [
        ("minimal function", "top10(sum:svcname by {region})"),
        ("multiple args", "top(sum:svcname by {region},5,'max','desc')"),
        ("corner case: whitespace", "top(  sum:svcname  ,  5  ,  'max'  ,  'desc'  )"),
        ("corner case: double quotes", 'top(sum:svcname by {region},5,"max","desc")'),
    ]

    formula_cases = [
        ("in parens", "(avg:svcname.requests)"),
        ("corner case: whitespace", "(  avg:svcname.requests   )"),
        ("int and query", "100 * avg:svcname.requests"),
        ("corner case: negative int", "-100 * avg:svcname.requests"),
        ("corner case: whitespace", "100   *   avg:svcname.requests"),
        ("corner case: two queries", "sum:svcname.requests * avg:svcname.requests"),
        ("parens and int", "(100 * avg:svcname.requests) + 1"),
        ("nested func", "top(abs(avg:svcname.requests))"),
        ("suspect: comma sep", "sum:svcname.requests, avg:svcname.requests"),
    ]

    cases = single_query_cases + function_cases + formula_cases

    parser = QueryParser()

    failed = 0
    for desc, case in cases:
        try:
            parser.parse_st(case)
        except (IncompleteParseError, ParseError) as exc:
            failed += 1
            sys.stderr.write("Failed case: %r: %r:\n%s\n\n" % (desc, case, exc))

    assert failed == 0
