#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

from os.path import abspath, dirname, join

_name = 'immutablecollections'

with open(join(dirname(abspath(__file__)), _name, 'version.py')) as version_file:
    exec(compile(version_file.read(), "version.py", 'exec'))

setup(name=_name,
      version=version,
      author='Ryan Gabbard <gabbard@isi.edu> and Constantine Lignos <lignos@isi.edu>',
      author_email='gabbard@isi.edu',
      description='Immutable Collections (inspired by Google Guava)',
      url='https://github.com/isi-vista/immutablecollections',
      packages=['immutablecollections'],
      package_data={'immutablecollections': ['py.typed']},
      # 3.6 and up, but not Python 4
      python_requires='~=3.6',
      install_requires=[
          'typing_extensions',
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ]
)
