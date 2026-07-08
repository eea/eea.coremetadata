"""Tests for the Publication type core metadata taxonomy."""

import unittest

from collective.taxonomy import PATH_SEPARATOR
from collective.taxonomy.interfaces import ITaxonomy
from eea.coremetadata.behaviors.metadata import CoreMetadata
from eea.coremetadata.metadata import ICoreMetadata
from eea.coremetadata.tests.base import FUNCTIONAL_TESTING
from plone.app.querystring.interfaces import IQueryField
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory


INDEX_NAME = "taxonomy_eeapublicationtypetaxonomy"
TAXONOMY_NAME = "collective.taxonomy.eeapublicationtypetaxonomy"
EXPECTED_TERMS = [
    ("briefing", "Briefing"),
    ("report", "Report"),
    ("corporate-report", "Corporate report"),
    ("joint-report", "Joint report"),
    ("technical-paper", "Technical paper"),
]


def term_pairs(vocabulary):
    """Return vocabulary terms as value/title pairs."""
    return [(term.value, term.title) for term in vocabulary]


class TestPublicationType(unittest.TestCase):
    """Publication type taxonomy integration."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_taxonomy_is_registered_with_expected_terms(self):
        taxonomy = queryUtility(ITaxonomy, name=TAXONOMY_NAME)

        self.assertIsNotNone(taxonomy)
        self.assertEqual(taxonomy.title, "EEA Publication Type Taxonomy")
        entries = [
            (identifier, path.split(PATH_SEPARATOR)[-1])
            for path, identifier in taxonomy.makeVocabulary("en").iterEntries()
        ]
        self.assertEqual(entries, EXPECTED_TERMS)

    def test_core_metadata_schema_exposes_publication_type_field(self):
        field = ICoreMetadata["publication_type"]

        self.assertFalse(field.required)
        self.assertEqual(field.title, "Publication type")
        self.assertEqual(field.vocabularyName, "publication_type_vocabulary")

    def test_publication_type_behavior_stores_value_on_context(self):
        self.portal.invokeFactory("Document", "publication-type-behavior")
        document = self.portal["publication-type-behavior"]
        behavior = CoreMetadata(document)

        behavior.publication_type = "report"

        self.assertEqual(behavior.publication_type, "report")
        self.assertEqual(document.publication_type, "report")

    def test_publication_type_vocabulary_returns_taxonomy_terms(self):
        factory = queryUtility(IVocabularyFactory, name="publication_type_vocabulary")

        self.assertIsNotNone(factory)
        self.assertEqual(term_pairs(factory(self.portal)), EXPECTED_TERMS)

    def test_publication_type_catalog_index_indexes_field_value(self):
        catalog = getToolByName(self.portal, "portal_catalog")
        self.assertIn(INDEX_NAME, catalog.indexes())
        self.assertIn(INDEX_NAME, catalog.schema())

        self.portal.invokeFactory("Document", "publication-type-catalog")
        document = self.portal["publication-type-catalog"]
        document.publication_type = "briefing"
        document.reindexObject()

        brains = catalog({INDEX_NAME: "briefing"})

        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getId, "publication-type-catalog")

    def test_index_vocabulary_returns_catalog_used_terms_only(self):
        catalog = getToolByName(self.portal, "portal_catalog")
        self.portal.invokeFactory("Document", "publication-type-index-vocab")
        document = self.portal["publication-type-index-vocab"]
        document.publication_type = "technical-paper"
        document.reindexObject()

        self.assertEqual(
            len(catalog({INDEX_NAME: "technical-paper"})),
            1,
        )

        factory = queryUtility(
            IVocabularyFactory, name="index_publication_type_vocabulary"
        )

        self.assertIsNotNone(factory)
        self.assertEqual(
            term_pairs(factory(self.portal)),
            [("technical-paper", "Technical paper")],
        )

    def test_querystring_registry_field_is_configured(self):
        registry = queryUtility(IRegistry)
        prefix = "plone.app.querystring.field.{0}".format(INDEX_NAME)
        records = registry.forInterface(IQueryField, prefix=prefix)

        self.assertEqual(records.title, "Publication type")
        self.assertTrue(records.enabled)
        self.assertTrue(records.sortable)
        self.assertEqual(records.group, "Taxonomy")
        self.assertEqual(records.vocabulary, "index_publication_type_vocabulary")
        self.assertEqual(
            records.operations,
            ["plone.app.querystring.operation.selection.is"],
        )


if __name__ == "__main__":
    unittest.main()
