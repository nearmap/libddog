# Datadog library and command line tools

[![Latest PyPI package version](https://badge.fury.io/py/libddog.svg)](https://pypi.org/project/libddog)
[![libddog tests](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml/badge.svg)](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml)


libddog allows you to define your metrics and dashboards in code and get the full benefit of a programming language to automate your monitoring setup.

```python
query = (Query("aws.elb.request_count")
        .filter(region="us-east-1")
        .agg("sum").by("availability-zone")
        .rollup("sum", 300))
```


![ELB request count](docs/assets/elb-reqs-graph.png)

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