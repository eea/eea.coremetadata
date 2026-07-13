"""Unit tests for publication type classification and helpers.

These tests cover pure functions from the publication type migration
that don't require a running Plone instance:

- iter_text
- report_value
- as_bool
- taxonomy_term_title
- classify_publication (using lightweight stub objects)
"""

import unittest

from collective.taxonomy import PATH_SEPARATOR

from eea.coremetadata.behaviors.vocabulary import taxonomy_term_title
from eea.coremetadata.browser.publication_type_migration import (
    as_bool,
    classify_publication,
    iter_text,
    report_value,
)


class TestIterText(unittest.TestCase):
    """Tests for iter_text recursive text extraction."""

    def test_string(self):
        self.assertEqual(list(iter_text("hello")), ["hello"])

    def test_list_of_strings(self):
        self.assertEqual(list(iter_text(["a", "b"])), ["a", "b"])

    def test_nested_list(self):
        self.assertEqual(list(iter_text(["a", ["b", "c"]])), ["a", "b", "c"])

    def test_dict(self):
        result = sorted(iter_text({"x": "a", "y": "b"}))
        self.assertEqual(result, ["a", "b"])

    def test_nested_dict(self):
        data = {"blocks": {"id1": "text1", "id2": {"sub": "text2"}}}
        result = sorted(iter_text(data))
        self.assertEqual(result, ["text1", "text2"])

    def test_tuple(self):
        self.assertEqual(list(iter_text(("a", "b"))), ["a", "b"])

    def test_set(self):
        result = sorted(iter_text({"a", "b"}))
        self.assertEqual(result, ["a", "b"])

    def test_empty_list(self):
        self.assertEqual(list(iter_text([])), [])

    def test_none(self):
        self.assertEqual(list(iter_text(None)), [])

    def test_deeply_nested(self):
        data = {"a": [{"b": ["c", "d"]}, "e"]}
        self.assertEqual(list(iter_text(data)), ["c", "d", "e"])


class TestReportValue(unittest.TestCase):
    """Tests for report_value string serialization."""

    def test_none(self):
        self.assertEqual(report_value(None), "")

    def test_string(self):
        self.assertEqual(report_value("briefing"), "briefing")

    def test_list(self):
        self.assertEqual(report_value(["a", "b"]), "a;b")

    def test_tuple(self):
        self.assertEqual(report_value(("a", "b")), "a;b")

    def test_set(self):
        result = report_value({"a", "b"})
        self.assertIn("a", result)
        self.assertIn("b", result)
        self.assertIn(";", result)

    def test_integer(self):
        self.assertEqual(report_value(42), "42")


class TestAsBool(unittest.TestCase):
    """Tests for as_bool query-string parser."""

    def test_true(self):
        self.assertTrue(as_bool("true"))

    def test_true_uppercase(self):
        self.assertTrue(as_bool("True"))

    def test_one(self):
        self.assertTrue(as_bool("1"))

    def test_yes(self):
        self.assertTrue(as_bool("yes"))

    def test_on(self):
        self.assertTrue(as_bool("on"))

    def test_false(self):
        self.assertFalse(as_bool("false"))

    def test_zero(self):
        self.assertFalse(as_bool("0"))

    def test_empty_string(self):
        self.assertFalse(as_bool(""))

    def test_no(self):
        self.assertFalse(as_bool("no"))

    def test_random_string(self):
        self.assertFalse(as_bool("banana"))


class TestTaxonomyTermTitle(unittest.TestCase):
    """Tests for taxonomy_term_title path parsing."""

    def test_single_term(self):
        path = PATH_SEPARATOR + "briefing"
        self.assertEqual(taxonomy_term_title(path), "briefing")

    def test_nested_term(self):
        path = PATH_SEPARATOR + "parent" + PATH_SEPARATOR + "child"
        self.assertEqual(taxonomy_term_title(path), "child")

    def test_deeply_nested(self):
        path = PATH_SEPARATOR + "a" + PATH_SEPARATOR + "b" + PATH_SEPARATOR + "c"
        self.assertEqual(taxonomy_term_title(path), "c")

    def test_strips_non_ascii(self):
        path = PATH_SEPARATOR + "r\xe9port"
        self.assertEqual(taxonomy_term_title(path), "rport")


class StubObject:
    """Minimal stand-in for a Plone content object."""

    def __init__(
        self,
        portal_type,
        text="",
        title="",
        description="",
        blocks=None,
        body=None,
        text_field=None,
    ):
        self.portal_type = portal_type
        self.title = title
        self.description = description
        self.blocks = blocks
        self.body = body
        if text_field is not None:
            self.text = text_field
        else:
            self.text = text


class TestClassifyPublication(unittest.TestCase):
    """Tests for classify_publication classification logic."""

    def test_briefing(self):
        obj = StubObject(portal_type="briefing")
        token, reason = classify_publication(obj)
        self.assertEqual(token, "briefing")
        self.assertIn("briefing", reason.lower())

    def test_web_report(self):
        obj = StubObject(portal_type="web_report")
        token, reason = classify_publication(obj)
        self.assertEqual(token, "report")
        self.assertIn("web_report", reason)

    def test_report_pdf_default(self):
        obj = StubObject(portal_type="report_pdf", text="A regular report")
        token, reason = classify_publication(obj)
        self.assertEqual(token, "report")
        self.assertIn("Remaining", reason)

    def test_report_pdf_corporate_phrase(self):
        obj = StubObject(
            portal_type="report_pdf",
            text="This is an EEA corporate report about something",
        )
        token, reason = classify_publication(obj)
        self.assertEqual(token, "corporate-report")
        self.assertIn("corporate report", reason)

    def test_report_pdf_issn(self):
        obj = StubObject(
            portal_type="report_pdf",
            text="Published with ISSN 3094-5976",
        )
        token, reason = classify_publication(obj)
        self.assertEqual(token, "corporate-report")
        self.assertIn("ISSN", reason)

    def test_report_pdf_issn_with_en_dash(self):
        obj = StubObject(
            portal_type="report_pdf",
            text="Published with ISSN 3094\u20135976",
        )
        token, reason = classify_publication(obj)
        self.assertEqual(token, "corporate-report")

    def test_report_pdf_phrase_and_issn(self):
        obj = StubObject(
            portal_type="report_pdf",
            text="EEA corporate report, ISSN 3094-5976",
        )
        token, reason = classify_publication(obj)
        self.assertEqual(token, "corporate-report")
        self.assertIn("corporate report", reason)
        self.assertIn("ISSN", reason)

    def test_unsupported_type(self):
        obj = StubObject(portal_type="document")
        token, reason = classify_publication(obj)
        self.assertIsNone(token)
        self.assertIn("Unsupported", reason)

    def test_classification_from_blocks(self):
        obj = StubObject(
            portal_type="report_pdf",
            blocks={
                "block-1": {"text": "EEA corporate report"},
            },
        )
        token, reason = classify_publication(obj)
        self.assertEqual(token, "corporate-report")

    def test_classification_from_description(self):
        obj = StubObject(
            portal_type="report_pdf",
            description="An EEA corporate report summary",
        )
        token, reason = classify_publication(obj)
        self.assertEqual(token, "corporate-report")


if __name__ == "__main__":
    unittest.main()
