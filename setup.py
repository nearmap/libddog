from setuptools import find_packages, setup
from pathlib import Path

import libddog

proj_dir = Path(__file__).parent
long_desc = (proj_dir / "README-PYPI.md").read_text()

setup(
    name="libddog",
    version=libddog.__version__,
    description="Datadog automation tool",
    long_description=long_desc,
    long_description_content_type='text/markdown',
    author="Martin Matusiak",
    author_email="martin.matusiak@nearmap.com",
    url="https://github.com/nearmap/libddog",
    license="MIT",
    packages=find_packages('.', exclude=('libtests', 'testdata', 'tests_*',)),
    package_dir={"": "."},
    package_data={
        "libddog": ["py.typed"],
        "libddog.parsing": ["grammar.txt"]
    },
    # NOTE: also cross check with requirements.txt
    install_requires=[
        "click>=8.0.0",
        "datadog>=0.41.0",
        "packaging>=21.0",
        "parsimonious>=0.8.0",
        "python-dateutil>=2.0.0",
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
