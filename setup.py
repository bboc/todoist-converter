#!/usr/bin/env python
from setuptools import setup, find_packages

VERSION = "1.0rc1"

install_requires = [
    # nothing
]

tests_require = [
    'nose',
]

if __name__ == "__main__":
    with open("README.md", "r") as fh:
        long_description = fh.read()
    setup(
        name="todoist-converter",
        version=VERSION,
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
