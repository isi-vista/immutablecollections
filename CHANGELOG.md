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
