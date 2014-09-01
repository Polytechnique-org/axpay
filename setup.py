#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.

import codecs
import os
import re
import sys

from setuptools import find_packages, setup

root_dir = os.path.abspath(os.path.dirname(__file__))


def get_version(package_name):
    version_re = re.compile(r"^__version__ = [\"']([\w_.-]+)[\"']$")
    package_components = package_name.split('.')
    init_path = os.path.join(root_dir, *(package_components + ['__init__.py']))
    with codecs.open(init_path, 'r', 'utf-8') as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.1.0'


PACKAGE = 'axpay'


setup(
    name=PACKAGE,
    version=get_version(PACKAGE),
    description="AXPay, a payment tracking system for AX/X.org",
    long_description=''.join(codecs.open('README.rst', 'r', 'utf-8').readlines()),
    author="Polytechnique.org's team",
    author_email="opensource+%s@polytechnique.org" % PACKAGE,
    license="GPLv3+",
    keywords=['payment', 'subscription', 'ax', 'Polytechnique.org'],
    url="https://github.com/Polytechnique-org/%s/" % PACKAGE,
    download_url="https://pypi.python.org/pypi/%s/" % PACKAGE,
    packages=find_packages(),
    platforms=["OS Independent"],
    install_requires=codecs.open('requirements.txt', 'r', 'utf-8').readlines(),
    setup_requires=[
        'setuptools>=0.8',
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: End Users/Dekstop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business:: Financial",
    ],
    test_suite='tests',
    zip_safe=False,
)

