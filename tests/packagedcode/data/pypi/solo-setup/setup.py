#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

test_requirements = [
    "black>=19.10b0",
    "flake8>=3.8.3",
    "flake8-debugger>=3.2.1",
]

dev_requirements = [
    *test_requirements,
    "wheel>=0.34.2",
]

requirements = [
    "cdp-backend[pipeline]==3.0.16",
    "cdp-scrapers>=0.4.0",
]

extra_requirements = {
    "test": test_requirements,
    "dev": dev_requirements,
    "all": [
        *requirements,
        *dev_requirements,
    ],
}

setup(
    author="Council Data Project Contributors",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
    ],
    description="Package containing the gather functions for Example.",
    install_requires=requirements,
    license="MIT license",
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="civic technology, open government",
    name="cdp-seattle-backend",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.9",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    url="https://github.com/CouncilDataProject/seattle",
    version="1.0.0",
    zip_safe=False,
)
