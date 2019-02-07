from collections.abc import Sequence
from unittest import TestCase

from immutablecollections import immutablelist, ImmutableList


class TestImmutableList(TestCase):
    def test_empty(self):
        empty = immutablelist()
        self.assertEqual(0, len(empty))
        empty2 = immutablelist([])
        self.assertEqual(0, len(empty2))
        self.assertEqual(empty, empty2)

    def test_empty_singleton(self):
        empty1 = immutablelist()
        empty2 = immutablelist()
        self.assertIs(empty1, empty2)
        empty4 = immutablelist(dict())
        self.assertIs(empty1, empty4)

    def test_basic(self):
        items = [1, 2, 3]
        list1 = immutablelist(items)
        self.assertEqual(list(list1), items)
        self.assertEqual(len(list1), 3)
        self.assertEqual(list1[0], 1)

    def test_return_identical_immutable(self):
        list1 = immutablelist([1, 2, 3])
        list2 = immutablelist(list1)
        self.assertIs(list1, list2)

    def test_singleton_empty(self):
        empty = immutablelist()
        empty2 = immutablelist()
        self.assertIs(empty, empty2)

    def test_hash_eq(self):
        list1 = immutablelist([1, 2, 3])
        list2 = immutablelist([1, 2, 3])
        list3 = immutablelist([3, 2, 1])

        self.assertEqual(list1, list2)
        self.assertNotEqual(list1, list3)

        val = object()
        d = {list1: val}
        self.assertEqual(d[list2], val)
        self.assertEqual(hash(list2), hash(list1))
        self.assertTrue(list3 not in d)

    def test_immutable(self):
        source = [1, 2, 3]
        list1 = immutablelist(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            list1.append(4)
        # Update doesn't affect original
        source.append(4)
        self.assertNotEqual(immutablelist(source), list1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableList([1, 2, 3])

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            immutablelist(7)

    def test_isinstance(self):
        list1 = immutablelist([1, 2, 3])
        self.assertTrue(isinstance(list1, Sequence))

    def test_slots(self):
        self.assertFalse(hasattr(immutablelist([1, 2, 3]), "__dict__"))

    def test_repr(self):
        self.assertEqual("i[1, 2, 3]", repr(immutablelist([1, 2, 3])))

    def test_str(self):
        self.assertEqual("[1, 2, 3]", str(immutablelist([1, 2, 3])))

    def test_slice(self):
        self.assertEqual(2, immutablelist([1, 2, 3])[1])
        self.assertEqual((2, 3), immutablelist([1, 2, 3])[1:])

    @staticmethod
    def type_annotations() -> str:
        # Just to check for mypy warnings
        list1 = immutablelist("a")
        return list1[0]
