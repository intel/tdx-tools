#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
from setuptools import find_packages, setup

def load_readme():
    with io.open("README.md", "rt", encoding="utf8") as f:
        readme = f.read()
    return readme

setup(
    name='tdvfkeyenroll',
    version='1.0.3',
    author='Min Xu',
    author_email='min.m.xu@intel.com',
    maintainer='mvp tdx stack',
    maintainer_email='jialei.feng@intel.com',
    description=('A tool to enroll keys into TDVF for secure boot.'),
    packages=['tdvfkeyenroll'],
    package_data={
        'tdvfkeyenroll': ['SecureBootEnable.bin']
    },
    include_package_data=True,
    python_requires=">=3.6",
    license='Apache',
    long_description=load_readme(),
    entry_points={
        "console_scripts": ["tdvfkeyenroll = tdvfkeyenroll.secure_boot:main"]
    },
)
