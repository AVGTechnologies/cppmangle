#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='cppmangle',
    version='0.1',

    description='A parser for mangled C++ names',
    author='AVG Technologies CZ, s.r.o.',
    url='https://github.com/AVGTechnologies/cppmangle',
    license='Apache 2.0',

    packages=['cppmangle'],
    entry_points={
        'console_scripts': [
            'cppdemangle=cppmangle.__main__:main'
            ]
        }
    )
