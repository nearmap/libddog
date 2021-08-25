# Datadog library and command line tools

[![Latest PyPI package version](https://badge.fury.io/py/libddog.svg)](https://pypi.org/project/libddog)
[![libddog tests](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml/badge.svg?branch=master)](https://github.com/nearmap/libddog/actions/workflows/github-actions.yml)


libddog lets you define your metrics and dashboards in code and get the full benefit of a programming language to automate your monitoring setup.

First you write the query:

```python
query = (Query("aws.elb.request_count")
        .filter(region="us-east-1")
        .agg("sum").by("availability-zone")
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

This gives you the widget you want, with all the parameters supported by the Datadog UI:

![ELB request count](docs/assets/elb-reqs-graph.png)



## Why libddog?

Monitoring tools like Datadog make it easy to experiment with different metrics and widgets, and create dashboards for many different visualizations of your systems. This is great for prototyping your monitoring setup, but it is not great for maintainability. Over time, as your team accumulates dashboards, they become a maintenance burden. Many of the graphs stop working because the metrics have changed, or the data shown isn't correct anymore. The enthusiasm that goes into creating the dashboards typically doesn't extend to maintaining their whole lifecycle. And let's be fair: it is not especially fun to manually change 20 graphs on a dashboard to update the name of a metric, change a tag, or update the aggregation or rollup parameters.

The thing is - in order to remain useful your dashboards need to keep pace with the continuous change in your systems. How can we make this easier?

Well, how do we manage this change in our systems? We architect our systems. We strive for single source of truth, modularity and code reuse. Why should we not do the same with our monitoring architecture? 

How would we apply these ideas to dashboards?

Let's start by defining the name of the metric in one place and reuse that. Every graph on every dashboard should use this definition when doing anything with ELB request counts:

```python
elb_requests = Query("aws.elb.request_count")
```

Next, the choice of aggregation function has to do with how we want to combine this metric coming from multiple nodes. If you want to compute a global count of requests we would sum them. But if we do that we should also make sure that we aggregate the samples in time the same way, and apply a rollup which agrees with the aggregation:

```python
elb_requests_totals = elb_requests.agg("sum").rollup("sum")
```

Finally, the way we want to visualize these requests counts 