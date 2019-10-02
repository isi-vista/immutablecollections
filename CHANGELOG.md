Immutablecollections 0.9.0 (2019-10-02)
=======================================

New Features
------------

- `ImmutableSet` now implements the same methods as the standard library `frozenset`. Added the `issubset`, `issuperset`, and `symmetric_difference` convenience methods that wrap `<=`, `>=`, and `^`, respectively, and the shallow `copy` method. (`#61 <https://github.com/isi-vista/immutablecollections/issues/61>`_)


Bug Fixes
---------

- Slicing of `ImmutableSet`s that only contain a single element is implemented. (`#23 <https://github.com/isi-vista/immutablecollections/issues/23>`_)


Immutablecollections 0.8.0 (2019-07-25)
=======================================

New Features
------------

- Add workarounds for mypy problems with attrs type converters and generics.  This is to workaround python/mypy#5738 and  python-attrs/attrs#519 . (`#59 <https://github.com/isi-vista/immutablecollections/pull/59>`_)


Immutablecollections 0.7.0 (2019-05-21)
=======================================

Backward-incompatible Changes
-----------------------------

- `ImmutableList` has been removed in favor of `tuple`. Now that we are no longer targeting support for runtime type-checking of collections, `ImmutableList` had no advantage over `tuple` for any purpose. (`#42 <https://github.com/isi-vista/immutablecollections/issues/42>`_)


Bug Fixes
---------

- immutableset can now be created from KeysView, ItemsView if dict iteration is deterministic. (`#35 <https://github.com/isi-vista/immutablecollections/issues/35>`_)


Immutablecollections 0.6.0 (2019-02-19)
=======================================

New Features
------------

- ImmutableDict supports equality comparison with `dict`.
  ImmutableSet supports equality comparison with `set` and `frozenset`. (`#33 <https://github.com/isi-vista/immutablecollections/issues/33>`_)


Immutablecollections 0.5.0 (2019-02-07)
=======================================

New Features
------------

- Distribute type information (PEP 561) (`#29 <https://github.com/isi-vista/immutablecollections/issues/29>`_)


Immutablecollections 0.4.0 (2019-02-07)
=======================================

Backward-incompatible Changes
-----------------------------

- Removes `.as_list()` from `ImmutableSet`.
  It is no longer needed since `ImmutableSet` extends `Sequence`. (`#12 <https://github.com/isi-vista/immutablecollections/issues/12>`_)


New Features
------------

- Adds module-level factory methods for all collections (e.g. `immutableset(...)`).
  These should be preferred over builders and `.of` methods. (`#12 <https://github.com/isi-vista/immutablecollections/issues/12>`_)


Immutablecollections 0.3.0 (2018-11-01)
=======================================

New Features
------------

- Started using towncrier to generate a changelog (`#6 <https://github.com/isi-vista/immutablecollections/issues/6>`_)
- Support inversion of MultiDicts (`#8 <https://github.com/isi-vista/immutablecollections/issues/8>`_)
