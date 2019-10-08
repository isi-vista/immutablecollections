"""
immutablecollections provides immutable collections in the spirit of
those provided by Google's Guava in Java.

Each immutable collection can be created with the `of` static method,
which accepts an iterable of the same type as the equivalent mutable
built-in. For example, an ImmutableDict will accept a dict or an
iterable of (key, value) tuples, just like the dict builtin.
Empty collections can be created with the `empty` static method. There
is a dedicated method for an empty collection to avoid the potential
bugs enabled by allowing `of` to be provided the value None or no
arguments.

Immutable collections efficiently reuse objects when possible. In the
following example, x and y will refer to the same object:
x = immutableset([1, 2, 3])
y = immutableset(x)

Immutable collections will also compare equal with objects of the same
fundamental type. For example, immutableset([1, 2, 3]) is equal to
frozenset([1, 2, 3]), both of which are equal to the regular set {1, 2, 3}.

isort:skip_file
"""

# Easiest to just use the same exception
# noinspection PyUnresolvedReferences
from attr.exceptions import FrozenInstanceError

from immutablecollections._immutableset import (
    ImmutableSet,
    immutableset,
    immutableset_from_unique_elements,
)
from immutablecollections._immutabledict import (
    ImmutableDict,
    immutabledict,
    immutabledict_from_unique_keys,
)
from immutablecollections._immutablemultidict import (
    ImmutableListMultiDict,
    ImmutableSetMultiDict,
    immutablelistmultidict,
    immutablesetmultidict,
)
from immutablecollections.immutablecollection import ImmutableCollection
from immutablecollections.version import version as __version__
