from typing import List

from dashboards import aws_elb

from libddog.dashboards import Dashboard


def get_dashboards() -> List[Dashboard]:
    dashes = [
        aws_elb.get_dashboard(),
    ]

    return dashes
