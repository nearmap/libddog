# Datadog library and command line tools

[![Latest PyPI package version](https://badge.fury.io/py/libddog.svg)](https://pypi.org/project/libddog)
[![libddog tests](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml/badge.svg?branch=master)](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml)


libddog lets you define your metrics and dashboards in code and get the full benefit of a programming language to automate your monitoring setup.

First you write the query:

```python
query = (Query("aws.elb.request_count")
        .filter(region="us-east-1")
        .agg("sum").by("availability-zone")
        .rollup("sum", 300))

# produces:
#   sum:aws.elb.request_count{region:us-east-1}
#    by {availability-zone}.as_count().rollup(sum, 300)
```

The query language closely resembles the Datadog syntax, but because it's Python code and not just a string it is validated and known to be well formed at definition time.

Then you define what the widget looks like:

```python
Timeseries(
    title="ELB: total requests by AZ every 5min",
    requests=[
        Request(
            queries=[query],
            display_type=DisplayType.BARS,
        ),
    ],
    size=Size(height=3, width=5),
)
```

This gives you the widget you want, with all the parameters supported by the Datadog UI:

![ELB request count](docs/assets/elb-reqs-graph.png)