#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

export_packages =  find_packages(where='.', include=('immutablecollections'))

setup(name='immutablecollections',
      version='0.1.0',
      description='Immutable Collections (inspired by Google Guava)',
      packages=export_packages,
      # 3.6 and up, but not Python 4
      python_requires='~=3.6',
      install_requires=[
          'attrs>=17.3.0',
          'frozendict',
          'typing_extensions',
          'sortedcontainers>=1.5.9'
      ],
      )
