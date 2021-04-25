#!/usr/bin/env python
# mypy: ignore-errors
#
#
# Speedo - it
#
#

import os

from setuptools import setup, find_namespace_packages
from speedo_common.version import speedo_version as __version__


def get_requirements(filename: str):
    """Build the requirements list from the filename"""
    requirements_list = []
    with open(filename, "r") as reqs:
        for install in reqs:
            requirements_list.append(install.strip())
    return requirements_list


if os.getenv("SPEEDO_TARGET", "") == "client":
    setup(
        name="Speedo - python client library",
        version=__version__,
        description="Speedo - python client library",
        url="https://www.nokx.ch",
        author="nokx",
        author_email="info@nokx.ch",
        packages=find_namespace_packages(include=["speedo_client.*"])
        + find_namespace_packages(include=["speedo_common.*"])
        + ["speedo_client", "speedo_common"],
        install_requires=get_requirements("requirements_client.txt"),
        python_requires=">=3",
    )
elif os.getenv("SPEEDO_TARGET", "") == "server":
    setup(
        name="Speedo - server",
        version=__version__,
        description="Speedo - a fast RESTful web API",
        url="https://www.nokx.ch",
        author="nokx",
        author_email="info@nokx.ch",
        scripts=["scripts/speedo"],
        package_data={"": ["alembic.ini"]},
        packages=find_namespace_packages(include=["speedo_server.*"])
        + find_namespace_packages(include=["speedo_common.*"])
        + ["speedo_server", "speedo_common"],
        install_requires=get_requirements("requirements_server.txt"),
        python_requires=">=3",
    )
else:
    raise EnvironmentError(
        "Please target the following environment variable"
        "\n\n\t"
        "$ export SPEEDO_TARGET=server # or"
        "\n\t"
        "$ export SPEEDO_TARGET=client"
        "\n\n"
        "before running the installation"
        "\n\n\t"
        "$ python setup.py install --prefix=/tmp/destination"
        "\n\t"
        "$ # you can use pip instead (use a virtualenv)"
        "\n\t"
        "$ pip install ."
        "\n"
    )
