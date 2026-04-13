"""Unit tests for eea.coremetadata pure functions

These tests cover pure functions that don't require Plone context:
- seq_strip
- tuplize
"""

import unittest
from eea.coremetadata.metadata import seq_strip, tuplize


class TestSeqStrip(unittest.TestCase):
    """Tests for seq_strip function"""

    def test_strip_list(self):
        result = list(seq_strip(["  a  ", "  b  "]))
        self.assertEqual(result, ["a", "b"])

    def test_strip_tuple(self):
        result = seq_strip(("  a  ", "  b  "))
        self.assertEqual(result, ("a", "b"))

    def test_custom_stripper(self):
        result = list(seq_strip(["A", "B"], stripper=str.lower))
        self.assertEqual(result, ["a", "b"])

    def test_empty_list(self):
        result = list(seq_strip([]))
        self.assertEqual(result, [])

    def test_unsupported_type(self):
        with self.assertRaises(ValueError):
            seq_strip("not a sequence")


class TestTuplize(unittest.TestCase):
    """Tests for tuplize function"""

    def test_tuple_passthrough(self):
        result = tuplize("test", ("  a  ", "  b  "))
        self.assertEqual(result, ("a", "b"))

    def test_list_to_tuple(self):
        result = tuplize("test", ["  a  ", "  b  "])
        self.assertEqual(result, ("a", "b"))

    def test_string_split(self):
        result = tuplize("test", "a b c")
        self.assertEqual(result, ("a", "b", "c"))

    def test_custom_splitter(self):
        result = tuplize("test", "a,b,c", splitter=lambda x: x.split(","))
        self.assertEqual(result, ("a", "b", "c"))

    def test_unsupported_type(self):
        with self.assertRaises(ValueError):
            tuplize("test", 42)

    def test_empty_string(self):
        result = tuplize("test", "")
        self.assertEqual(result, ())

    def test_empty_tuple(self):
        result = tuplize("test", ())
        self.assertEqual(result, ())


if __name__ == "__main__":
    unittest.main()