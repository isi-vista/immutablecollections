from typing import Sequence, AbstractSet
from unittest import TestCase
import faulthandler
from immutablecollections import immutableset, immutablesetbuilder, ImmutableSet

faulthandler.enable()


class TestImmutableSet(TestCase):
    def test_set_construction(self):
        immutableset([1, 2, 3])

    def testIsSet(self):
        self.assertTrue(isinstance(immutableset([1,2,3]), AbstractSet))

    #def testIsSequence(self):
    #    self.assertTrue(isinstance(immutableset([1,2,3]), Sequence))

    def test_ordered_builder(self):
        sort_key = lambda x: x[1]
        builder = immutablesetbuilder(order_key=sort_key)
        builder.add("hello")
        builder.add("hallo")
        built = builder.build()
        self.assertEqual("hallo", built[0])
        self.assertEqual("hello", built[1])

    def test_empty_is_singleton(self):
        builder1 = immutablesetbuilder()
        set1 = builder1.build()
        builder2 = immutablesetbuilder()
        set2 = builder2.build()
        set3 = immutableset([])
        set4 = immutableset([])
        self.assertIs(set1, set2)
        self.assertIs(set2, set3)
        self.assertIs(set3, set4)

    def test_basic_equality(self):
        a = immutableset([1, 2, 3])
        b = immutableset([3, 2, 1])
        self.assertEqual(a, b)

    def test_add_all(self):
        builder = immutablesetbuilder()
        builder.add(3)
        builder.add_all([2, 1])

        ref = immutableset([1, 2, 3])

        self.assertEqual(ref, builder.build())

    def test_basic_union(self):
        a = immutableset([1, 2, 3])
        b = immutableset([3, 4, 5])
        ref = immutableset([1, 2, 3, 4, 5])
        self.assertEqual(ref, a.union(b))

    def test_basic_intersection(self):
        a = immutableset([1, 2, 3])
        b = immutableset([3, 4, 5])
        ref = immutableset([3])
        self.assertEqual(ref, a.intersection(b))
