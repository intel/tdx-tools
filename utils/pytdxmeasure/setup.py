"""
Setup script
"""
import io
from setuptools import setup


def load_readme():
    """
    Load content from README.md
    """
    with io.open('README.md', 'rt', encoding='utf8') as fobj:
        readme = fobj.read()
    return readme


def load_requirements():
    """
    Load content from requirements.txt
    """
    with open('requirements.txt', encoding='utf-8') as fobj:
        return fobj.read().splitlines()


setup(
    name='pytdxmeasure',
    version='0.0.3',
    packages=['pytdxmeasure'],
    package_data={
        '': ['tdx_eventlogs.sh', 'tdx_tdreport.sh', 'tdx_verify_rtmr.sh']
    },
    include_package_data=True,
    python_requires='>=3.6.8',
    license='Apache License 2.0',
    scripts=['tdx_eventlogs.sh', 'tdx_tdreport.sh', 'tdx_verify_rtmr.sh'],
    long_description=load_readme(),
    install_requires=load_requirements()
)
