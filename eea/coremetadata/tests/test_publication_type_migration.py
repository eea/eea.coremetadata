"""Tests for the Publication type content migration BrowserView."""

import csv
import io
import unittest

from eea.coremetadata.browser.publication_type_migration import (
    FIELD_NAME,
    PublicationTypeMigrationView,
    classify_publication,
)
from eea.coremetadata.tests.base import FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.fti import DexterityFTI


TAXONOMY_BEHAVIOR = "collective.taxonomy.generated.eeapublicationtypetaxonomy"


class MigrationViewWithoutCommits(PublicationTypeMigrationView):
    """Keep test changes in the test transaction."""

    def commit(self):
        pass


class TestPublicationTypeMigration(unittest.TestCase):
    """Publication migration rules and report integration."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.add_type("briefing")
        self.add_type("report_pdf")
        self.add_type("web_report")

    def add_type(self, portal_type):
        fti = DexterityFTI(portal_type)
        self.portal.portal_types._setObject(portal_type, fti)
        fti.klass = "plone.dexterity.content.Item"
        fti.behaviors = ("plone.basic", TAXONOMY_BEHAVIOR)

    def add_content(self, portal_type, content_id, blocks=None):
        self.portal.invokeFactory(portal_type, content_id, title=content_id)
        obj = self.portal[content_id]
        if blocks is not None:
            obj.blocks = blocks
        obj.reindexObject()
        return obj

    def test_classification_rules(self):
        briefing = self.add_content("briefing", "briefing-item")
        web_report = self.add_content("web_report", "web-report-item")
        report = self.add_content("report_pdf", "report-item")
        phrase = self.add_content(
            "report_pdf",
            "corporate-phrase",
            {"one": {"plaintext": "EEA Corporate Report 01/2025"}},
        )
        issn = self.add_content(
            "report_pdf",
            "corporate-issn",
            {"one": {"plaintext": "ISSN: 3094-5976"}},
        )

        self.assertEqual(classify_publication(briefing)[0], "briefing")
        self.assertEqual(classify_publication(web_report)[0], "report")
        self.assertEqual(classify_publication(report)[0], "report")
        self.assertEqual(classify_publication(phrase)[0], "corporate-report")
        self.assertEqual(classify_publication(issn)[0], "corporate-report")

    def test_migration_is_idempotent_and_reports_each_route(self):
        briefing = self.add_content("briefing", "briefing-to-migrate")
        report = self.add_content(
            "report_pdf",
            "corporate-to-migrate",
            {"one": {"plaintext": "EEA corporate report"}},
        )
        manually_classified = self.add_content("report_pdf", "manual-classification")
        setattr(manually_classified, FIELD_NAME, "joint-report")
        manually_classified.reindexObject()

        view = MigrationViewWithoutCommits(self.portal, self.request)
        rows = view.migrate()
        by_path = {row["path"]: row for row in rows}

        self.assertEqual(getattr(briefing, FIELD_NAME), "briefing")
        self.assertEqual(getattr(report, FIELD_NAME), "corporate-report")
        self.assertEqual(getattr(manually_classified, FIELD_NAME), "joint-report")
        self.assertEqual(by_path["/plone/briefing-to-migrate"]["status"], "updated")
        self.assertEqual(
            by_path["/plone/corporate-to-migrate"]["content_type"],
            "report_pdf",
        )
        self.assertIn(
            "EEA corporate report",
            by_path["/plone/corporate-to-migrate"]["reason"],
        )
        self.assertEqual(
            by_path["/plone/manual-classification"]["status"],
            "skipped-existing-classification",
        )

        second_rows = view.migrate()
        second_by_path = {row["path"]: row for row in second_rows}
        self.assertEqual(
            second_by_path["/plone/briefing-to-migrate"]["status"],
            "already-classified",
        )

    def test_csv_download_contains_required_audit_columns(self):
        self.add_content("web_report", "csv-report")
        view = MigrationViewWithoutCommits(self.portal, self.request)
        rows = view.migrate(dry_run=True)
        body = view.csv_response(rows, dry_run=True)
        reader = csv.DictReader(io.StringIO(body.lstrip("\ufeff")))
        report_rows = list(reader)

        self.assertEqual(len(report_rows), 1)
        self.assertEqual(report_rows[0]["status"], "would-update")
        self.assertEqual(report_rows[0]["content_type"], "web_report")
        self.assertEqual(report_rows[0]["proposed_publication_type"], "report")
        self.assertEqual(
            self.request.response.getHeader("Content-Type"),
            "text/csv; charset=utf-8",
        )
        self.assertIn(
            "publication-type-dry-run-",
            self.request.response.getHeader("Content-Disposition"),
        )


if __name__ == "__main__":
    unittest.main()
