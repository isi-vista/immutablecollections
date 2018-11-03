# python-immutables

Native implementation of an Python immutable set which preserves insertion order.

I used `pyrsistent`'s `PVector` as a model of how to write a Python native module, so there is a lot of code borrowed from there.

# Local dev environment
* Make a Python 3.6 virtualenv. (Right now I'm only working with Python 3.6; I'll look into other things later.)
* At least on my Mac, `python setup.py install` just works (you may need XCode tools installed).
* You can now do `from immutablecollections import immutableset, immutablesetbuilder` from the interpreter in that virtual env for testing.

I edit the code in IntelliJ's CLion (at least until my 30 day trial runs out...).  At the moment the CMakeLists are hard-coded for my include directories; fixing that is TODO.
