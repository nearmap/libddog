from typing import List

from dashboards import aws_ec2

from libddog.dashboards import Dashboard


def get_dashboards() -> List[Dashboard]:
    dashes = [
        aws_ec2.get_dashboard(),
    ]

    return dashes
