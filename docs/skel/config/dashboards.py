from typing import List

from libddog.dashboards import Dashboard

from dashboards import aws_ec2


def get_dashboards() -> List[Dashboard]:
    dashes = [
        aws_ec2.get_dashboard(),
    ]

    return dashes
