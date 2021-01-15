#!/usr/bin/env python
import pathlib
from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader("version", "starlette_request_id/version.py").load_module()


_ROOT = pathlib.Path(__file__).parent

with open(str(_ROOT / "README.rst")) as f:
    readme = f.read()

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Operating System :: POSIX",
    "Topic :: System :: Networking",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Environment :: Console",
    "Intended Audience :: Developers",
]

setup(
    name="starlette-request-id",
    version=str(version.VERSION),
    license="Apache License, Version 2.0",
    description="Localisation helper for starlette",
    long_description=readme,
    long_description_content_type="text/x-rst",
    author="Pavel Liashkov",
    author_email="pavel.liashkov@protonmail.com",
    maintainer="Pavel Liashkov",
    maintainer_email="pavel.liashkov@protonmail.com",
    download_url="https://pypi.python.org/pypi/starlette-request-id",
    url="https://github.com/bigbag/starlette-request-id",
    platforms=["POSIX"],
    classifiers=CLASSIFIERS,
    python_requires=">=3.7",
    install_requires=["starlette==0.14.1"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="",
)
