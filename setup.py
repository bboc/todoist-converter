#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    # nothing
]

tests_require = [
    'nose',
]

setup(
    name="todoist-converter",
    version="0.4",
    author="Bernhard Bockelbrink",
    author_email="bernhard.bockelbrink@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bboc/todoist-converter",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="nose.collector",
    entry_points={
        'console_scripts': [
            'tdconv = tdconv.tdconv:main',
        ],
    }
)
