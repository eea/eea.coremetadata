"""Functional tests for the Publication type migration report."""

import csv
import io
import unittest

from AccessControl import getSecurityManager
from DateTime import DateTime
from eea.coremetadata.browser.publication_type_migration import FIELD_NAME
from eea.coremetadata.browser.publication_type_migration import REPORT_FIELDS
from eea.coremetadata.browser.publication_type_migration import (
    PublicationTypeMigrationView,
)
from eea.coremetadata.setuphandlers import PUBLICATION_CONTENT_TYPES
from eea.coremetadata.tests.base import FUNCTIONAL_TESTING
from eea.coremetadata.upgrades.to_62 import to_62
from Acquisition import aq_base
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.fti import DexterityFTIModificationDescription
from plone.dexterity.fti import DexterityFTI
from ZODB.POSException import ConflictError
from zope.lifecycleevent import modified

LEGACY_FIELD_NAME = "taxonomy_eeapublicationtypetaxonomy"


class MigrationViewWithoutCommits(PublicationTypeMigrationView):
    """Keep migration changes inside the test transaction."""

    def commit(self):
        """Do not commit the shared test transaction."""


class MigrationViewWithBrains(MigrationViewWithoutCommits):
    """Run migration against explicitly supplied test brains."""

    brains = ()

    def catalog_brains(self):
        """Return the test-specific brain sequence."""
        return self.brains


class BrokenBrain:
    """Minimal catalog brain which fails while loading its object."""

    portal_type = "briefing"
    UID = "broken-uid"
    Title = "Broken publication"

    def __init__(self, exception):
        self.exception = exception

    def getPath(self):
        return "/plone/broken-publication"

    def getURL(self):
        return "http://nohost/plone/broken-publication"

    def getObject(self):
        raise self.exception


class TestPublicationTypeMigrationIntegration(unittest.TestCase):
    """Verify content updates, audit rows, and CSV responses."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        for portal_type in PUBLICATION_CONTENT_TYPES:
            self.add_type(portal_type)
        to_62(self.portal.portal_setup)

    def add_type(self, portal_type):
        """Create a minimal Dexterity item type."""
        fti = DexterityFTI(portal_type)
        self.portal.portal_types._setObject(portal_type, fti)
        fti = self.portal.portal_types[portal_type]
        fti.klass = "plone.dexterity.content.Item"
        fti.behaviors = ()
        return fti

    def add_content(self, portal_type, content_id, blocks=None):
        """Create and index one publication candidate."""
        self.portal.invokeFactory(
            portal_type,
            content_id,
            title=content_id,
        )
        item = self.portal[content_id]
        if blocks is not None:
            item.blocks = blocks
        item.reindexObject()
        return item

    def rows_by_id(self, rows):
        """Index report rows by the final path segment."""
        return {row["path"].rsplit("/", 1)[-1]: row for row in rows}

    def test_dry_run_reports_without_mutating_content(self):
        item = self.add_content("briefing", "dry-run-briefing")
        view = MigrationViewWithoutCommits(self.portal, self.request)

        rows = view.migrate(dry_run=True)
        row = self.rows_by_id(rows)["dry-run-briefing"]

        self.assertIsNone(getattr(aq_base(item), FIELD_NAME, None))
        self.assertEqual(row["run_mode"], "dry-run")
        self.assertEqual(row["status"], "would-update")
        self.assertEqual(row["content_type"], "briefing")
        self.assertEqual(row["proposed_publication_type"], "briefing")
        self.assertEqual(row["final_publication_type"], "")

    def test_migration_updates_each_classification_route(self):
        briefing = self.add_content("briefing", "briefing-item")
        web_report = self.add_content("web_report", "web-report-item")
        regular_report = self.add_content("report_pdf", "regular-report")
        phrase_report = self.add_content(
            "report_pdf",
            "corporate-phrase",
            {"one": {"plaintext": "EEA corporate report 01/2025"}},
        )
        issn_report = self.add_content(
            "report_pdf",
            "corporate-issn",
            {"one": {"plaintext": "ISSN 3094-5976"}},
        )
        view = MigrationViewWithoutCommits(self.portal, self.request)

        rows = view.migrate()
        by_id = self.rows_by_id(rows)

        self.assertEqual(briefing.publication_type, "briefing")
        self.assertEqual(web_report.publication_type, "report")
        self.assertEqual(regular_report.publication_type, "report")
        self.assertEqual(phrase_report.publication_type, "corporate-report")
        self.assertEqual(issn_report.publication_type, "corporate-report")
        self.assertEqual(by_id["briefing-item"]["status"], "updated")
        self.assertIn(
            "EEA corporate report",
            by_id["corporate-phrase"]["reason"],
        )
        self.assertIn("ISSN", by_id["corporate-issn"]["reason"])

    def test_migration_updates_modification_date(self):
        item = self.add_content("briefing", "modified-briefing")
        old_modified = DateTime("2000/01/01")
        item.setModificationDate(old_modified)
        item.reindexObject(idxs=["modified"])
        view = MigrationViewWithoutCommits(self.portal, self.request)

        view.migrate()

        self.assertGreater(item.modified(), old_modified)
        brain = self.portal.portal_catalog(UID=item.UID())[0]
        self.assertEqual(brain.modified, item.modified())

    def test_migration_records_authenticated_user_in_editing_history(self):
        fti = self.portal.portal_types["briefing"]
        fti.behaviors = tuple(fti.behaviors) + ("plone.versioning",)
        modified(
            fti,
            DexterityFTIModificationDescription("behaviors", ""),
        )
        repository = self.portal.portal_repository
        repository.setVersionableContentTypes(
            list(repository.getVersionableContentTypes()) + ["briefing"]
        )
        repository.addPolicyForContentType(
            "briefing",
            "at_edit_autoversion",
        )
        item = self.add_content("briefing", "versioned-briefing")
        item.publication_type = "briefing"
        view = MigrationViewWithoutCommits(self.portal, self.request)
        authenticated_user = getSecurityManager().getUser().getUserName()

        view.migrate()

        version = repository.retrieve(item)
        history = repository.getHistoryMetadata(item)
        metadata = history.retrieve(version.version_id)["metadata"]["sys_metadata"]
        self.assertEqual(version.version_id, 1)
        self.assertEqual(version.object.publication_type, "briefing")
        self.assertEqual(metadata["principal"], authenticated_user)

    def test_existing_new_field_value_is_overwritten(self):
        item = self.add_content("report_pdf", "manual-classification")
        item.publication_type = "joint-report"
        item.reindexObject()
        view = MigrationViewWithoutCommits(self.portal, self.request)

        dry_run_row = self.rows_by_id(view.migrate(dry_run=True))[
            "manual-classification"
        ]
        self.assertEqual(item.publication_type, "joint-report")
        self.assertEqual(dry_run_row["status"], "would-update")

        row = self.rows_by_id(view.migrate())["manual-classification"]

        self.assertEqual(item.publication_type, "report")
        self.assertEqual(row["status"], "updated")
        self.assertEqual(row["previous_publication_type"], "joint-report")
        self.assertEqual(row["final_publication_type"], "report")

    def test_legacy_generated_field_is_ignored(self):
        item = self.add_content("report_pdf", "legacy-classification")
        setattr(item, LEGACY_FIELD_NAME, "joint-report")
        item.reindexObject()
        view = MigrationViewWithoutCommits(self.portal, self.request)

        row = self.rows_by_id(view.migrate())["legacy-classification"]

        self.assertEqual(getattr(item, LEGACY_FIELD_NAME), "joint-report")
        self.assertEqual(item.publication_type, "report")
        self.assertEqual(row["previous_publication_type"], "")
        self.assertEqual(row["proposed_publication_type"], "report")
        self.assertEqual(row["final_publication_type"], "report")
        self.assertEqual(row["status"], "updated")
        self.assertIn("Remaining Report", row["reason"])

    def test_second_run_refreshes_already_classified_content(self):
        item = self.add_content("web_report", "idempotent-report")
        view = MigrationViewWithoutCommits(self.portal, self.request)

        first = self.rows_by_id(view.migrate())["idempotent-report"]
        old_modified = DateTime("2000/01/01")
        item.setModificationDate(old_modified)
        item.reindexObject(idxs=["modified"])
        second = self.rows_by_id(view.migrate())["idempotent-report"]

        self.assertEqual(item.publication_type, "report")
        self.assertEqual(first["status"], "updated")
        self.assertEqual(second["status"], "updated")
        self.assertGreater(item.modified(), old_modified)

    def test_missing_behavior_is_reported_without_writing(self):
        item = self.add_content("briefing", "missing-behavior")
        fti = self.portal.portal_types["briefing"]
        fti.behaviors = ()
        modified(
            fti,
            DexterityFTIModificationDescription("behaviors", ""),
        )
        view = MigrationViewWithoutCommits(self.portal, self.request)

        row = self.rows_by_id(view.migrate())["missing-behavior"]

        self.assertIsNone(getattr(aq_base(item), FIELD_NAME, None))
        self.assertEqual(row["status"], "missing-behavior")
        self.assertEqual(
            row["error"],
            "Publication type behavior is not enabled",
        )

    def test_catalog_candidates_are_sorted_by_path(self):
        self.add_content("web_report", "z-report")
        self.add_content("briefing", "a-briefing")
        view = MigrationViewWithoutCommits(self.portal, self.request)

        paths = [brain.getPath() for brain in view.catalog_brains()]

        self.assertEqual(paths, sorted(paths))

    def test_object_error_is_reported_and_migration_continues(self):
        view = MigrationViewWithBrains(self.portal, self.request)
        view.brains = (BrokenBrain(ValueError("Cannot load publication")),)

        rows = view.migrate()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "error")
        self.assertEqual(rows[0]["error"], "Cannot load publication")
        self.assertEqual(rows[0]["uid"], "broken-uid")

    def test_conflict_error_is_not_swallowed(self):
        view = MigrationViewWithBrains(self.portal, self.request)
        view.brains = (BrokenBrain(ConflictError()),)

        with self.assertRaises(ConflictError):
            view.migrate()

    def test_csv_contains_all_audit_columns_and_headers(self):
        self.add_content("web_report", "csv-report")
        view = MigrationViewWithoutCommits(self.portal, self.request)
        rows = view.migrate(dry_run=True)

        body = view.csv_response(rows, dry_run=True)
        reader = csv.DictReader(io.StringIO(body.lstrip("\ufeff")))
        report_rows = list(reader)

        self.assertEqual(reader.fieldnames, list(REPORT_FIELDS))
        self.assertEqual(len(report_rows), 1)
        self.assertEqual(report_rows[0]["status"], "would-update")
        self.assertEqual(report_rows[0]["content_type"], "web_report")
        self.assertEqual(
            report_rows[0]["proposed_publication_type"],
            "report",
        )
        self.assertEqual(
            self.request.response.getHeader("Content-Type"),
            "text/csv; charset=utf-8",
        )
        self.assertIn(
            "publication-type-dry-run-",
            self.request.response.getHeader("Content-Disposition"),
        )
        self.assertEqual(
            self.request.response.getHeader("X-Migration-Total"),
            "1",
        )
        self.assertEqual(
            self.request.response.getHeader("X-Migration-Updated"),
            "0",
        )
        self.assertEqual(
            self.request.response.getHeader("X-Migration-Errors"),
            "0",
        )

    def test_call_uses_request_dry_run_flag(self):
        self.add_content("briefing", "request-dry-run")
        self.request.form["dry_run"] = "true"
        view = MigrationViewWithoutCommits(self.portal, self.request)

        body = view()

        self.assertIn("would-update", body)
        self.assertIn("request-dry-run", body)
        self.assertIn(
            "publication-type-dry-run-",
            self.request.response.getHeader("Content-Disposition"),
        )


if __name__ == "__main__":
    unittest.main()
