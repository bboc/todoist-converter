#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="todoist-converter",
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'tdconv = tdconv.tdconv:main',
        ],
    }
)
