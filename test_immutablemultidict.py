from unittest import TestCase

from flexnlp.utils.immutablecollections.immutablemultidict import ImmutableSetMultiDict


class TestImmutableMultiDict(TestCase):
    def test_set_repr(self):
        self.assertEqual("i{1: {2, 3}, 4: {5, 6}}",
                         repr(ImmutableSetMultiDict.of(
                             {1: [2, 3], 4: [5, 6]})))

    def test_set_str(self):
        self.assertEqual("{1: {2, 3}, 4: {5, 6}}",
                         str(ImmutableSetMultiDict.of(
                             {1: [2, 3], 4: [5, 6]})))
