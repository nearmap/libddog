# Datadog library and command line tools

[![Latest PyPI package version](https://badge.fury.io/py/libddog.svg)](https://pypi.org/project/libddog)
[![libddog tests](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml/badge.svg?branch=master)](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml)


libddog lets you define your metrics and dashboards in code and get the full benefit of a programming language to automate your monitoring setup.

First you write the query:

```python
query = (Query("aws.elb.request_count")
        .filter(region="us-east-1")
        .agg("sum").by("availability-zone").as_count()
        .rollup("sum", 5 * 60))

# produces:
#   sum:aws.elb.request_count{region:us-east-1}
#    by {availability-zone}.as_count().rollup(sum, 300)
```

The query language closely resembles the Datadog syntax, but because it's Python code and not just a string it is validated and known to be well formed at definition time.

Then you define what the graph looks like:

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

This gives you the widget you want, with all the parameters supported by the Datadog UI.

Learn more in the **[User guide](https://github.com/nearmap/libddog/blob/master/docs/USER_GUIDE.md)**.



## The state of the project

libddog is a young project and currently supports a small but useful subset of dashboard functionality. See the **[Feature support](https://github.com/nearmap/libddog/blob/master/docs/FEATURE_SUPPORT.md)** page for details.

We plan to support more dashboard features over time. We also plan to support monitors.

Want to know what's new in the project? Read the **[CHANGELOG](https://github.com/nearmap/libddog/blob/master/CHANGELOG.md)**.

Want to contribute? Start by reading the **[Maintainer guide](https://github.com/nearmap/libddog/blob/master/docs/MAINTAINER_GUIDE.md)**.
