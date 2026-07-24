"""Integration tests for the managed Publication type field."""

import unittest
from unittest.mock import Mock
from unittest.mock import patch

from collective.taxonomy import PATH_SEPARATOR
from collective.taxonomy.interfaces import ITaxonomy
from eea.coremetadata.behaviors.publication_type import IPublicationType
from eea.coremetadata.setuphandlers import (
    GENERATED_PUBLICATION_TYPE_BEHAVIOR,
)
from eea.coremetadata.setuphandlers import GENERATED_PUBLICATION_TYPE_FIELD
from eea.coremetadata.setuphandlers import PUBLICATION_CONTENT_TYPES
from eea.coremetadata.setuphandlers import PUBLICATION_TYPE_BEHAVIOR
from eea.coremetadata.setuphandlers import enable_publication_type_behavior
from eea.coremetadata.tests.base import INTEGRATION_TESTING
from eea.coremetadata.upgrades.to_62 import to_62
from plone.app.querystring.interfaces import IQueryField
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.behavior.interfaces import IBehavior
from plone.dexterity.fti import DexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory


INDEX_NAME = "publication_type"
TAXONOMY_NAME = "collective.taxonomy.eeapublicationtypetaxonomy"
QUERYSTRING_PREFIX = "plone.app.querystring.field.publication_type"
GENERATED_QUERYSTRING_PREFIX = (
    "plone.app.querystring.field.taxonomy_eeapublicationtypetaxonomy"
)
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


class TestPublicationTypeIntegration(unittest.TestCase):
    """Verify taxonomy, behavior, catalog, and upgrade integration."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = getToolByName(self.portal, "portal_catalog")
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def add_type(self, portal_type, behaviors=()):
        """Create a minimal Dexterity item type."""
        fti = DexterityFTI(portal_type)
        self.portal.portal_types._setObject(portal_type, fti)
        fti = self.portal.portal_types[portal_type]
        fti.klass = "plone.dexterity.content.Item"
        fti.behaviors = tuple(behaviors)
        return fti

    def add_publication_types(self, behaviors=()):
        """Create all publication FTIs used by the upgrade."""
        return {
            portal_type: self.add_type(portal_type, behaviors)
            for portal_type in PUBLICATION_CONTENT_TYPES
        }

    def test_taxonomy_has_expected_identity_and_terms(self):
        taxonomy = queryUtility(ITaxonomy, name=TAXONOMY_NAME)

        self.assertIsNotNone(taxonomy)
        self.assertEqual(taxonomy.title, "EEA Publication Type Taxonomy")

        entries = [
            (identifier, path.split(PATH_SEPARATOR)[-1])
            for path, identifier in taxonomy.makeVocabulary("en").iterEntries()
        ]
        self.assertEqual(entries, EXPECTED_TERMS)

    def test_dedicated_behavior_exposes_required_simple_field(self):
        behavior = queryUtility(IBehavior, name=PUBLICATION_TYPE_BEHAVIOR)
        field = behavior.interface["publication_type"]

        self.assertIsNotNone(behavior)
        self.assertIs(behavior.interface, IPublicationType)
        self.assertEqual(list(behavior.interface.names()), ["publication_type"])
        self.assertTrue(field.required)
        self.assertEqual(field.vocabularyName, "publication_type_vocabulary")

    def test_full_vocabulary_uses_managed_taxonomy(self):
        factory = queryUtility(
            IVocabularyFactory,
            name="publication_type_vocabulary",
        )

        self.assertIsNotNone(factory)
        self.assertEqual(term_pairs(factory(self.portal)), EXPECTED_TERMS)

    def test_upgrade_is_registered_from_61_to_62(self):
        setup = self.portal.portal_setup
        profile_id = "eea.coremetadata:default"
        setup.setLastVersionForProfile(profile_id, "6.1")

        groups = setup.listUpgrades(profile_id)
        steps = []
        for group in groups:
            steps.extend(group if isinstance(group, list) else [group])

        self.assertTrue(
            any(
                step["ssource"] == "6.1" and step["sdest"] == "6.2"
                for step in steps
            )
        )

    def test_upgrade_enables_behavior_only_on_publication_types(self):
        target_ftis = self.add_publication_types()
        other_fti = self.add_type("unrelated_type")

        to_62(self.portal.portal_setup)

        for fti in target_ftis.values():
            self.assertIn(PUBLICATION_TYPE_BEHAVIOR, fti.behaviors)
        self.assertNotIn(PUBLICATION_TYPE_BEHAVIOR, other_fti.behaviors)

    def test_behavior_activation_is_idempotent(self):
        target_ftis = self.add_publication_types()

        to_62(self.portal.portal_setup)
        to_62(self.portal.portal_setup)

        self.assertEqual(enable_publication_type_behavior(self.portal), [])
        for fti in target_ftis.values():
            self.assertEqual(
                fti.behaviors.count(PUBLICATION_TYPE_BEHAVIOR),
                1,
            )

    def test_upgrade_removes_generated_behavior_from_every_type(self):
        target_ftis = self.add_publication_types(
            behaviors=(GENERATED_PUBLICATION_TYPE_BEHAVIOR,),
        )
        unrelated = self.add_type(
            "legacy_publication_type",
            behaviors=(GENERATED_PUBLICATION_TYPE_BEHAVIOR,),
        )

        to_62(self.portal.portal_setup)

        for fti in list(target_ftis.values()) + [unrelated]:
            self.assertNotIn(
                GENERATED_PUBLICATION_TYPE_BEHAVIOR,
                fti.behaviors,
            )

    def test_upgrade_removes_generated_catalog_data(self):
        if GENERATED_PUBLICATION_TYPE_FIELD not in self.catalog.indexes():
            self.catalog.addIndex(
                GENERATED_PUBLICATION_TYPE_FIELD,
                KeywordIndex(GENERATED_PUBLICATION_TYPE_FIELD),
            )
        if GENERATED_PUBLICATION_TYPE_FIELD not in self.catalog.schema():
            self.catalog.addColumn(GENERATED_PUBLICATION_TYPE_FIELD)

        to_62(self.portal.portal_setup)

        self.assertNotIn(
            GENERATED_PUBLICATION_TYPE_FIELD,
            self.catalog.indexes(),
        )
        self.assertNotIn(
            GENERATED_PUBLICATION_TYPE_FIELD,
            self.catalog.schema(),
        )

    def test_upgrade_removes_generated_querystring_records(self):
        registry = queryUtility(IRegistry)
        self.assertTrue(
            any(
                name.startswith(GENERATED_QUERYSTRING_PREFIX)
                for name in registry.records
            )
        )

        to_62(self.portal.portal_setup)

        self.assertFalse(
            any(
                name.startswith(GENERATED_QUERYSTRING_PREFIX)
                for name in registry.records
            )
        )

    def test_querystring_field_uses_simple_index(self):
        registry = queryUtility(IRegistry)
        records = registry.forInterface(
            IQueryField,
            prefix=QUERYSTRING_PREFIX,
        )

        self.assertEqual(records.title, "Publication type")
        self.assertTrue(records.enabled)
        self.assertTrue(records.sortable)
        self.assertEqual(records.group, "Taxonomy")
        self.assertEqual(
            records.vocabulary,
            "index_publication_type_vocabulary",
        )
        self.assertFalse(records.fetch_vocabulary)
        self.assertEqual(
            records.operations,
            ["plone.app.querystring.operation.selection.is"],
        )

    def test_catalog_indexes_simple_field(self):
        self.add_publication_types()
        to_62(self.portal.portal_setup)
        self.portal.invokeFactory(
            "briefing",
            "indexed-briefing",
            title="Indexed briefing",
        )
        item = self.portal["indexed-briefing"]
        item.publication_type = "briefing"
        item.reindexObject()

        brains = self.catalog(publication_type="briefing")

        self.assertIn(INDEX_NAME, self.catalog.indexes())
        self.assertIn(INDEX_NAME, self.catalog.schema())
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getId, "indexed-briefing")
        self.assertEqual(brains[0].publication_type, "briefing")

    def test_upgrade_reindexes_simple_field(self):
        self.add_publication_types()
        catalog = Mock(wraps=self.catalog)

        with patch(
            "eea.coremetadata.upgrades.to_62.getToolByName",
            return_value=catalog,
        ):
            to_62(self.portal.portal_setup)

        catalog.reindexIndex.assert_called_once_with(
            INDEX_NAME,
            None,
        )

    def test_index_vocabulary_returns_only_values_used_in_catalog(self):
        self.add_publication_types()
        to_62(self.portal.portal_setup)
        self.portal.invokeFactory(
            "web_report",
            "technical-paper",
            title="Technical paper",
        )
        item = self.portal["technical-paper"]
        item.publication_type = "technical-paper"
        item.reindexObject()
        factory = queryUtility(
            IVocabularyFactory,
            name="index_publication_type_vocabulary",
        )

        self.assertEqual(
            len(self.catalog(publication_type="technical-paper")),
            1,
        )
        self.assertIn(
            "technical-paper",
            self.catalog.uniqueValuesFor(INDEX_NAME),
        )
        self.assertEqual(
            term_pairs(factory(self.portal)),
            [("technical-paper", "Technical paper")],
        )


if __name__ == "__main__":
    unittest.main()
