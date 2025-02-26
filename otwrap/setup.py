# coding: utf8
"""
Setup script for otwrap
============================
This script allows to install otwrap within the Python environment.
Usage
-----
::
    python setup.py install
"""

import re
import os
from setuptools import setup, find_packages

# Get the version from __init__.py
path = os.path.join(os.path.dirname(__file__), 'otwrap', '__init__.py')
with open(path) as f:
    version_file = f.read()

version = re.search(r"^\s*__version__\s*=\s*['\"]([^'\"]+)['\"]",
                    version_file, re.M)
if version:
    version = version.group(1)
else:
    raise RuntimeError("Unable to find version string.")

# Long description
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='otwrap',
    version=version,
    license='LGPLv3+',
    author="Elias Fekhari",
    author_email='elias.fekhari@edf.fr',
    packages=['otwrap'],
    keywords=['OpenTURNS', 'HPC'],
    description="Simplifies the evaluation of numerical simulation models on high performance computing facilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
          "openturns>=1.20", 
      ],
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
    ],

)