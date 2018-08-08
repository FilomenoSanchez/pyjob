"""Job Management Controller"""

__author__ = "Felix Simkovic"
__version__ = "1.0"

from distutils.util import convert_path

import os
import sys

try:
    from setuptools import setup
except ImportError:
    sys.exit("Please install setuptools first!")


def readme():
    with open('README.rst', 'r') as f_in:
        return f_in.read()


def version():
    """Get the current PyJob version"""
    main_ns = {}
    ver_path = convert_path(os.path.join('pyjob', 'version.py'))
    with open(ver_path) as f_in:
        exec(f_in.read(), main_ns)
    return main_ns['__version__']


AUTHOR = "Felix Simkovic"
AUTHOR_EMAIL = "felixsimkovic@me.com"
DESCRIPTION = __doc__.replace("\n", "")
LICENSE = "MIT License"
LONG_DESCRIPTION = readme()
PACKAGE_DIR = "pyjob"
PACKAGE_NAME = "pyjob"
URL = "https://github.com/fsimkovic/pyjob"
VERSION = version()

PACKAGES = [
    'pyjob',
]

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
]

ENTRY_POINTS = {'console_scripts': ['pyjob = pyjob.__main__:main']}

setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    name=PACKAGE_NAME,
    description=DESCRIPTION,
    entry_points=ENTRY_POINTS,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    version=VERSION,
    url=URL,
    packages=PACKAGES,
    package_dir={PACKAGE_NAME: PACKAGE_DIR},
    classifiers=CLASSIFIERS,
    setup_requires=['pytest-runner'],
    tests_require=['codecov', 'pytest', 'pytest-cov', 'pytest-pep8'],
    zip_safe=False,
)
