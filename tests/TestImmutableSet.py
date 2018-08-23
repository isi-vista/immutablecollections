from unittest import TestCase
import faulthandler
from immutablecollections import immutableset, immutablesetbuilder

faulthandler.enable()


class TestImmutableSet(TestCase):
    def test_set_construction(self):
        immutableset([1,2,3])

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
