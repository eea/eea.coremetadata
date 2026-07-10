"""Classify existing publications and return a CSV migration report."""

import csv
import logging
import re
from collections import Counter
from collections.abc import Mapping
from datetime import datetime
from datetime import timezone
from io import StringIO

import transaction
from Acquisition import aq_base
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from Products.Five import BrowserView
from ZODB.POSException import ConflictError
from zope.schema import getFields


logger = logging.getLogger(__name__)

FIELD_NAME = "taxonomy_eeapublicationtypetaxonomy"
PORTAL_TYPES = ("briefing", "report_pdf", "web_report")
BATCH_SIZE = 50

CORPORATE_REPORT_PATTERN = re.compile(r"\beea\s+corporate\s+report\b", re.I)
CORPORATE_ISSN_PATTERN = re.compile(r"3094[-\u2010-\u2013\u2212]5976")
TEXT_FIELDS = ("title", "description", "blocks", "text", "body")

REPORT_FIELDS = (
    "run_mode",
    "status",
    "path",
    "url",
    "uid",
    "title",
    "content_type",
    "previous_publication_type",
    "proposed_publication_type",
    "final_publication_type",
    "reason",
    "error",
)


def iter_text(value):
    """Yield text recursively from block data and rich text values."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, RichTextValue):
        yield value.raw
    elif isinstance(value, Mapping):
        for nested_value in value.values():
            yield from iter_text(nested_value)
    elif isinstance(value, (list, tuple, set)):
        for nested_value in value:
            yield from iter_text(nested_value)


def publication_text(obj):
    """Return the page text used by the Report (PDF) migration rules."""
    values = []
    base = aq_base(obj)
    for field_name in TEXT_FIELDS:
        if hasattr(base, field_name):
            values.extend(iter_text(getattr(base, field_name)))
    return "\n".join(values)


def classify_publication(obj):
    """Return the target taxonomy token and the matching migration rule."""
    portal_type = getattr(obj, "portal_type", "")
    if portal_type == "briefing":
        return "briefing", "Content type briefing maps to Briefing"
    if portal_type == "web_report":
        return "report", "Content type web_report maps to Report"
    if portal_type != "report_pdf":
        return None, "Unsupported content type"

    text = publication_text(obj)
    phrase_match = bool(CORPORATE_REPORT_PATTERN.search(text))
    issn_match = bool(CORPORATE_ISSN_PATTERN.search(text))
    if phrase_match and issn_match:
        reason = 'Report (PDF) contains "EEA corporate report" and ISSN 3094-5976'
        return "corporate-report", reason
    if phrase_match:
        return (
            "corporate-report",
            'Report (PDF) contains "EEA corporate report"',
        )
    if issn_match:
        return "corporate-report", "Report (PDF) contains ISSN 3094-5976"
    return "report", "Remaining Report (PDF) maps to Report"


def supports_publication_type(obj):
    """Check that the generated taxonomy behavior is enabled for the type."""
    try:
        return any(FIELD_NAME in getFields(schema) for schema in iterSchemata(obj))
    except TypeError:
        return False


def report_value(value):
    """Return a stable string representation for a taxonomy value."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(item) for item in value)
    return str(value)


def as_bool(value):
    """Parse a query-string boolean value."""
    return str(value).lower() in ("1", "true", "yes", "on")


class PublicationTypeMigrationView(BrowserView):
    """Migrate publication types and download one report row per item."""

    def __call__(self):
        dry_run = as_bool(self.request.form.get("dry_run", False))
        rows = self.migrate(dry_run=dry_run)
        return self.csv_response(rows, dry_run=dry_run)

    def catalog_brains(self):
        """Return all publication candidates in deterministic path order."""
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.unrestrictedSearchResults(portal_type=PORTAL_TYPES)
        return sorted(brains, key=lambda brain: brain.getPath())

    def migrate(self, dry_run=False):
        """Classify candidates, preserving values already set by editors."""
        rows = []
        for index, brain in enumerate(self.catalog_brains(), start=1):
            row = self.base_report_row(brain, dry_run)
            savepoint = None
            try:
                obj = brain.getObject()
                row["url"] = obj.absolute_url()
                row["title"] = getattr(obj, "title", row["title"])
                target, reason = classify_publication(obj)
                row["proposed_publication_type"] = target or ""
                row["reason"] = reason

                if not target:
                    row["status"] = "unclassified"
                elif not supports_publication_type(obj):
                    row["status"] = "missing-behavior"
                    row["error"] = "Publication type taxonomy behavior is not enabled"
                else:
                    current = getattr(aq_base(obj), FIELD_NAME, None)
                    row["previous_publication_type"] = report_value(current)
                    row["final_publication_type"] = report_value(current)
                    if current == target:
                        row["status"] = "already-classified"
                    elif current:
                        row["status"] = "skipped-existing-classification"
                        row["reason"] += "; existing value preserved"
                    elif dry_run:
                        row["status"] = "would-update"
                    else:
                        savepoint = transaction.savepoint(optimistic=True)
                        setattr(obj, FIELD_NAME, target)
                        obj.reindexObject()
                        row["final_publication_type"] = target
                        row["status"] = "updated"
            except ConflictError:
                if savepoint is not None:
                    savepoint.rollback()
                raise
            except Exception as error:  # noqa: B902 - migration must continue
                if savepoint is not None:
                    savepoint.rollback()
                row["status"] = "error"
                row["error"] = str(error)
                logger.exception("Could not classify %s", row["path"])

            rows.append(row)
            if not dry_run and index % BATCH_SIZE == 0:
                self.commit()

        if not dry_run:
            self.commit()

        counts = Counter(row["status"] for row in rows)
        logger.info("Publication type migration finished: %s", dict(counts))
        return rows

    def commit(self):
        """Commit a migration batch; isolated for transaction-safe tests."""
        transaction.commit()

    def base_report_row(self, brain, dry_run):
        """Build report data available without loading the object."""
        return {
            "run_mode": "dry-run" if dry_run else "migration",
            "status": "",
            "path": brain.getPath(),
            "url": brain.getURL(),
            "uid": getattr(brain, "UID", ""),
            "title": getattr(brain, "Title", ""),
            "content_type": getattr(brain, "portal_type", ""),
            "previous_publication_type": "",
            "proposed_publication_type": "",
            "final_publication_type": "",
            "reason": "",
            "error": "",
        }

    def csv_response(self, rows, dry_run=False):
        """Return an Excel-friendly UTF-8 CSV as a browser download."""
        output = StringIO()
        output.write("\ufeff")
        writer = csv.DictWriter(output, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        suffix = "dry-run" if dry_run else "migration"
        filename = "publication-type-{}-{}.csv".format(suffix, timestamp)
        response = self.request.response
        response.setHeader("Content-Type", "text/csv; charset=utf-8")
        response.setHeader(
            "Content-Disposition", 'attachment; filename="{}"'.format(filename)
        )

        counts = Counter(row["status"] for row in rows)
        response.setHeader("X-Migration-Total", str(len(rows)))
        response.setHeader("X-Migration-Updated", str(counts["updated"]))
        response.setHeader("X-Migration-Errors", str(counts["error"]))
        return output.getvalue()
