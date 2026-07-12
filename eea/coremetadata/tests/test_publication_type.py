"""Tests for the Publication type core metadata taxonomy."""

import unittest

from collective.taxonomy import PATH_SEPARATOR
from collective.taxonomy.interfaces import ITaxonomy
from eea.coremetadata.metadata import ICoreMetadata
from eea.coremetadata.setuphandlers import enable_publication_type_behavior
from eea.coremetadata.setuphandlers import PUBLICATION_CONTENT_TYPES
from eea.coremetadata.setuphandlers import PUBLICATION_TYPE_BEHAVIOR
from eea.coremetadata.tests.base import FUNCTIONAL_TESTING
from eea.coremetadata.upgrades.to_62 import to_62
from plone.app.querystring.interfaces import IQueryField
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.behavior.interfaces import IBehavior
from plone.dexterity.fti import DexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.schema import getFields
from zope.schema.interfaces import IVocabularyFactory


INDEX_NAME = "taxonomy_eeapublicationtypetaxonomy"
TAXONOMY_NAME = "collective.taxonomy.eeapublicationtypetaxonomy"
TAXONOMY_BEHAVIOR_NAME = PUBLICATION_TYPE_BEHAVIOR
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

    def add_type(self, portal_type, with_publication_type=True):
        """Add a minimal Dexterity type for taxonomy integration tests."""
        fti = DexterityFTI(portal_type)
        self.portal.portal_types._setObject(portal_type, fti)
        fti.klass = "plone.dexterity.content.Item"
        behaviors = ["plone.basic"]
        if with_publication_type:
            behaviors.append(TAXONOMY_BEHAVIOR_NAME)
        fti.behaviors = tuple(behaviors)
        return fti

    def test_taxonomy_is_registered_with_expected_terms(self):
        taxonomy = queryUtility(ITaxonomy, name=TAXONOMY_NAME)

        self.assertIsNotNone(taxonomy)
        self.assertEqual(taxonomy.title, "EEA Publication Type Taxonomy")
        entries = [
            (identifier, path.split(PATH_SEPARATOR)[-1])
            for path, identifier in taxonomy.makeVocabulary("en").iterEntries()
        ]
        self.assertEqual(entries, EXPECTED_TERMS)

        behavior = queryUtility(IBehavior, name=TAXONOMY_BEHAVIOR_NAME)
        self.assertIsNotNone(behavior)
        self.assertTrue(behavior.is_required)
        self.assertTrue(behavior.interface[INDEX_NAME].required)

    def test_core_metadata_does_not_duplicate_taxonomy_field(self):
        self.assertNotIn("publication_type", getFields(ICoreMetadata))

    def test_upgrade_enables_behavior_on_publication_content_types(self):
        for portal_type in PUBLICATION_CONTENT_TYPES:
            self.add_type(portal_type, with_publication_type=False)

        to_62(self.portal.portal_setup)
        to_62(self.portal.portal_setup)

        self.assertEqual(enable_publication_type_behavior(self.portal), [])

        for portal_type in PUBLICATION_CONTENT_TYPES:
            fti = self.portal.portal_types[portal_type]
            self.assertEqual(fti.behaviors.count(TAXONOMY_BEHAVIOR_NAME), 1)

    def test_upgrade_from_61_to_62_is_registered(self):
        setup = self.portal.portal_setup
        profile_id = "eea.coremetadata:default"
        setup.setLastVersionForProfile(profile_id, "6.1")

        groups = setup.listUpgrades(profile_id)
        steps = []
        for group in groups:
            steps.extend(group if isinstance(group, list) else [group])

        self.assertTrue(
            any(step["ssource"] == "6.1" and step["sdest"] == "6.2" for step in steps)
        )

    def test_publication_type_catalog_index_indexes_field_value(self):
        catalog = getToolByName(self.portal, "portal_catalog")
        self.assertIn(INDEX_NAME, catalog.indexes())
        self.assertIn(INDEX_NAME, catalog.schema())

        self.add_type("briefing")
        self.portal.invokeFactory("briefing", "publication-type-catalog")
        document = self.portal["publication-type-catalog"]
        setattr(document, INDEX_NAME, "briefing")
        document.reindexObject()

        brains = catalog({INDEX_NAME: "briefing"})

        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getId, "publication-type-catalog")

    def test_index_vocabulary_returns_catalog_used_terms_only(self):
        catalog = getToolByName(self.portal, "portal_catalog")
        self.add_type("web_report")
        self.portal.invokeFactory("web_report", "publication-type-index-vocab")
        document = self.portal["publication-type-index-vocab"]
        setattr(document, INDEX_NAME, "technical-paper")
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
