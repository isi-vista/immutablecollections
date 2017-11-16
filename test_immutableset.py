from collections.abc import Set
from unittest import TestCase

from flexnlp.util.immutablecollections import ImmutableSet


class TestImmutableSet(TestCase):

    def test_empty_set(self):
        empty = ImmutableSet.empty()
        self.assertEqual(set(empty), set())

    def test_basic(self):
        source = {1, 2, 3}
        set1 = ImmutableSet.of(source)
        self.assertEqual(set(set1), source)
        self.assertEqual(len(set1), 3)
        self.assertTrue(1 in set1)
        self.assertFalse(4 in set1)

    def test_return_identical_immutable(self):
        set1 = ImmutableSet.of([1, 2, 3])
        set2 = ImmutableSet.of(set1)
        self.assertIs(set1, set2)

    def test_singleton_empty(self):
        empty = ImmutableSet.empty()
        empty2 = ImmutableSet.empty()
        self.assertIs(empty, empty2)

    def test_hash_eq(self):
        set1 = ImmutableSet.of({1, 2, 3})
        set2 = ImmutableSet.of({1, 2, 3})
        set3 = ImmutableSet.of({1, 2})

        self.assertEqual(set1, set2)
        self.assertNotEqual(set1, set3)

        val = object()
        d = {set1: val}
        self.assertEqual(d[set2], val)
        self.assertEqual(hash(set2), hash(set1))
        self.assertTrue(set3 not in d)

    def test_immutable(self):
        source = {1, 2, 3}
        set1 = ImmutableSet.of(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            set1.add(4)
        # Update doesn't affect original
        source.add(4)
        self.assertNotEqual(ImmutableSet.of(source), set1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableSet([1, 2, 3])

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            ImmutableSet.of(7)

    def test_init(self):
        source = [1, 2, 3]
        # Able to use a non-set iterable
        set1 = ImmutableSet.of(source)
        set2 = ImmutableSet.of(set(source))
        self.assertEqual(set1, set2)

    def test_unhashable(self):
        source = [[1, 2, 3]]
        # Cannot create using unhashable values
        with self.assertRaises(TypeError):
            ImmutableSet.of(source)

    def test_isinstance(self):
        set1 = ImmutableSet.of([1, 2, 3])
        # Note that this is collections.abc.Set, not typing.Set,
        # which is mutable
        self.assertTrue(isinstance(set1, Set))

    def test_slots(self):
        self.assertFalse(hasattr(ImmutableSet.of([1, 2, 3]), '__dict__'))

    @staticmethod
    def type_annotations() -> int:
        # Just to check for mypy warnings
        source = {1, 2, 3}
        dict1 = ImmutableSet.of(source)
        return next(iter(dict1))
