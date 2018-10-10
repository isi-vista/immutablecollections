#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(name='immutablecollections',
      version='0.1.2',
      author='Ryan Gabbard <gabbard@isi.edu> and Constantine Lignos <lignos@isi.edu>',
      author_email='gabbard@isi.edu',
      description='Immutable Collections (inspired by Google Guava)',
      url='https://github.com/isi-vista/immutablecollections',
      packages=['immutablecollections'],
      # 3.6 and up, but not Python 4
      python_requires='~=3.6',
      install_requires=[
          'attrs>=17.3.0',
          'frozendict',
          'typing_extensions',
          'sortedcontainers>=1.5.9'
      ],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
      )
