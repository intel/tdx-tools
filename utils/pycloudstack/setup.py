"""
Setup scripts
"""
import os
from setuptools import setup


def read(fname):
    """
    Read specific file from current directory
    """
    return open(os.path.join(os.path.dirname(__file__), fname),
        encoding='utf-8').read()


def get_requirements():
    """
    Get requirements.
    """
    with open('requirements.txt', encoding='utf-8') as fobj:
        return fobj.read().splitlines()


setup(
    name="pycloudstack",
    version="0.0.5",
    author="Lu Ken",
    description=(
        "Abstract common cloud operators for both hypervisor and Kubernetes stacks"),
    license="Apache",
    packages=['pycloudstack'],
    package_data={'pycloudstack': ['templates/*.xml']},
    long_description=read('README.md'),
    install_requires=get_requirements(),
)
