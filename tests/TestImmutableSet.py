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
        dir(builder)
        builder.add("hello")
        builder.add("hallo")
        built = builder.build()
        self.assertEqual("hallo", built[0])
        self.assertEqual("hello", built[1])
