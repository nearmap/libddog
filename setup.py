from setuptools import find_packages, setup

import libddog

setup(
    name="libddog",
    version=libddog.__version__,
    description="Datadog dashboard automation tool",
    author="Martin Matusiak",
    author_email="martin.matusiak@nearmap.com",
    url="https://github.com/nearmap/libddog",
    packages=find_packages(".", exclude=("tests_*",)),
    package_dir={"": "."},
    package_data={"libddog": ["py.typed"]},
    install_requires=[
        "click==8.0.1",
        "datadog==0.41.0",
        "humanize==3.6.0",
        "python-dateutil==2.8.1",
    ],
    # don't install as zipped egg
    zip_safe=False,
    scripts=[
        "bin/ddog",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
