import platform

# these next two variables are used when guarding against the user
# initializing an ImmutableSet from something without deterministic
# iteration order

# In Python 3.7+, the spec guarantees dicts have an iteration order
# which matches insertion order
_PYTHON_VERSION_GUARANTEES_DETERMINISTIC_DICT_ITERATION = platform.python_version_tuple() >= (
    "3",
    "7",
    "0",
)

# we know CPython guarantees deterministic dict iteration order
# in 3.6+ as an implementation detail.  If other implementations
# guarantee this as well, we can add them here.
_PYTHON_IMPLEMENTATION_HAS_DETERMINISTIC_DICT_ITERATION = (
    platform.python_version_tuple() >= ("3", "6", "0")
    and platform.python_implementation() == "CPython"
)

DICT_ITERATION_IS_DETERMINISTIC = (
    _PYTHON_VERSION_GUARANTEES_DETERMINISTIC_DICT_ITERATION
    or _PYTHON_IMPLEMENTATION_HAS_DETERMINISTIC_DICT_ITERATION
)
