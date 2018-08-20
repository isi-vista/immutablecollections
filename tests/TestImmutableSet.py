from unittest import TestCase
import faulthandler
from immutablecollections import immutableset

faulthandler.enable()

class TestImmutableSet(TestCase):
    def test_set_construction(self):
        immutableset([1,2,3])
