import os
from setuptools import setup, Extension
import sys
import platform
import warnings
import codecs
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError
from distutils.errors import DistutilsPlatformError, DistutilsExecError

# readme_path = os.path.join(os.path.dirname(__file__), 'README.rst')
# with codecs.open(readme_path, encoding='utf8') as f:
#    readme = f.read()
readme = ""

extensions = []
if platform.python_implementation() == 'CPython':
    extensions = [Extension('immutablecollections', sources=['immutableset.c'])]


class custom_build_ext(build_ext):
    """Allow C extension building to fail."""

    warning_message = """
********************************************************************************
WARNING: Could not build the %s. 
         
         Pyrsistent will still work but performance may be degraded.
         
         %s
********************************************************************************
"""

    def run(self):
        try:
            build_ext.run(self)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError):
            e = sys.exc_info()[1]
            sys.stdout.write('%s\n' % str(e))
            warnings.warn(self.warning_message % ("Extension modules",
                                                  "There was an issue with "
                                                  "your platform configuration"
                                                  " - see above."))

    def build_extension(self, ext):
        name = ext.name
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError):
            e = sys.exc_info()[1]
            sys.stdout.write('%s\n' % str(e))
            warnings.warn(self.warning_message % ("The %s extension "
                                                  "module" % (name,),
                                                  "The output above "
                                                  "this warning shows how "
                                                  "the compilation "
                                                  "failed."))


setup(
    name='immutablecollections',
    version='0.1.0',
    description='Persistent/Functional/Immutable data structures',
    long_description="",
    author='Ryan Gabbard',
    author_email='ryan.gabbard@gmail.com',
    url='http://github.com/rgabbard/immutablecollections',
    license='MIT',
    py_modules=[],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    #    test_suite='tests',
    scripts=[],
    ext_modules=extensions,
    # cmdclass={"build_ext": custom_build_ext},
    install_requires=[],
    packages=[],
    package_data={
        'immutablecollections': ['py.typed']
    }
)
