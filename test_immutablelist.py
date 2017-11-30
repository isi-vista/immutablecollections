from collections.abc import Sequence
from unittest import TestCase

from flexnlp.util.immutablecollections import ImmutableList


class TestImmutableList(TestCase):

    def test_empty_list(self):
        empty = ImmutableList.empty()
        self.assertEqual(list(empty), [])

    def test_basic(self):
        items = [1, 2, 3]
        list1 = ImmutableList.of(items)
        self.assertEqual(list(list1), items)
        self.assertEqual(len(list1), 3)
        self.assertEqual(list1[0], 1)

    def test_return_identical_immutable(self):
        list1 = ImmutableList.of([1, 2, 3])
        list2 = ImmutableList.of(list1)
        self.assertIs(list1, list2)

    def test_singleton_empty(self):
        empty = ImmutableList.empty()
        empty2 = ImmutableList.empty()
        self.assertIs(empty, empty2)

    def test_hash_eq(self):
        list1 = ImmutableList.of([1, 2, 3])
        list2 = ImmutableList.of([1, 2, 3])
        list3 = ImmutableList.of([3, 2, 1])

        self.assertEqual(list1, list2)
        self.assertNotEqual(list1, list3)

        val = object()
        d = {list1: val}
        self.assertEqual(d[list2], val)
        self.assertEqual(hash(list2), hash(list1))
        self.assertTrue(list3 not in d)

    def test_immutable(self):
        source = [1, 2, 3]
        list1 = ImmutableList.of(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            list1.append(4)
        # Update doesn't affect original
        source.append(4)
        self.assertNotEqual(ImmutableList.of(source), list1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableList([1, 2, 3])

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            ImmutableList.of(7)

    def test_isinstance(self):
        list1 = ImmutableList.of([1, 2, 3])
        self.assertTrue(isinstance(list1, Sequence))

    def test_slots(self):
        self.assertFalse(hasattr(ImmutableList.of([1, 2, 3]), '__dict__'))

    def test_repr(self):
        self.assertEqual("i[1, 2, 3]", repr(ImmutableList.of([1, 2, 3])))

    def test_repr(self):
        self.assertEqual("[1, 2, 3]", str(ImmutableList.of([1, 2, 3])))

    @staticmethod
    def type_annotations() -> str:
        # Just to check for mypy warnings
        list1 = ImmutableList.of('a')
        return list1[0]
