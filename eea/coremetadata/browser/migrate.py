from plone.dexterity.utils import iterSchemataForType
import logging

from Acquisition import aq_self
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from eea.coremetadata.behaviors.vocabulary import get_vocabulary
from plone import api
from eea.coremetadata.metadata import ICoreMetadata

# from plone.behavior.interfaces import IBehavior
# from plone.dexterity.interfaces import IDexterityFTI
# from zope.component import getUtility


logger = logging.getLogger("eea.coremetadata")


VOCAB_NAME = "collective.taxonomy.eeaorganisationstaxonomy"


class OtherOrganisation(BrowserView):
    """ see #261751 """

    def __call__(self):
        types = getToolByName(self.context, 'portal_types').listTypeInfo()
        migrated_types = []

        for _type in types:
            portal_type = _type.getId()
            for schemata in iterSchemataForType(portal_type):
                if schemata is ICoreMetadata:
                    migrated_types.append(portal_type)

        vocabulary = get_vocabulary(self.context, VOCAB_NAME)

        org_translated = {key: val for val, key in vocabulary}
        self.migrate_portal_type(migrated_types, org_translated)

        return "Done"

    def migrate_portal_type(self, portal_types, org_translated):
        brains = api.content.find(context=self.context,
                                  portal_type=portal_types)

        for brain in brains:
            obj = brain.getObject()
            obj = aq_self(obj)
            orgs = getattr(obj, 'other_organisations', None)

            if orgs:
                translated = tuple([
                    org_translated[key].replace('\u241F', '')
                    for key in orgs
                    if key in org_translated
                ])
                obj.other_organisations = translated
                obj._p_changed = True
                obj.reindexObject()
                logger.info("Migrated organisations for obj (%s) - %s -> %s",
                            brain.getURL(), orgs, obj.other_organisations)
