#!/usr/bin/env python3
"""
Ghost Protocol Setup Script
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ghost-protocol",
    version="1.0.0",
    author="Ghost Protocol Team",
    author_email="team@ghostprotocol.dev",
    description="Python-based adversary simulation platform for security training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ghostprotocol/ghost-protocol",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gpserver=ghost_protocol.server.main:main",
            "ghost=ghost_protocol.client.main:main",
            "gpbeacon=ghost_protocol.beacon.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ghost_protocol": [
            "config/*.yaml",
            "templates/*.html",
            "static/*",
        ],
    },
)
