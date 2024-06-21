# pylint: disable=W1201, C0301, C0111, W0640, W1202
# -*- coding: utf-8 -*-
""" Upgrade to 3.6 """
import logging

from Products.CMFCore.utils import getToolByName
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
from Products.ZCatalog.Catalog import CatalogError
from plone.dexterity.utils import iterSchemataForType
from plone import api
from Acquisition import aq_self
from eea.coremetadata.behaviors.vocabulary import get_vocabulary
from eea.coremetadata.metadata import ICoreMetadata

logger = logging.getLogger("eea.coremetadata.upgrade")

VOCAB_NAME = "collective.taxonomy.eeaorganisationstaxonomy"
INDEX_NAME = "other_organisations"
OLD_INDEX_NAME = "taxonomy_eeaorganisationstaxonomy"


def to_36(context):
    catalog = getToolByName(context.aq_parent, "portal_catalog")

    idx_object = KeywordIndex(INDEX_NAME)

    try:
        catalog.addIndex(INDEX_NAME, idx_object)
    except CatalogError:
        logging.info(
            "Index {0} already exists, we hope it is proper configured".format(  # noqa: E501
                INDEX_NAME
            )  # noqa: E501
        )

    types = getToolByName(context, 'portal_types').listTypeInfo()
    migrated_types = []

    for _type in types:
        portal_type = _type.getId()
        for schemata in iterSchemataForType(portal_type):
            if schemata is ICoreMetadata:
                migrated_types.append(portal_type)

    vocabulary = get_vocabulary(context, VOCAB_NAME)

    org_translated = {key: val if ord(
        val[0]) < 255 else val[1:] for val, key in vocabulary}
    brains = api.content.find(portal_type=migrated_types)

    for brain in brains:
        try:
            obj = brain.getObject()
        except KeyError:
            logging.info("{0} was not found".format(brain.getURL(1)))
            continue
        obj = aq_self(obj)
        orgs = getattr(obj, 'other_organisations', None)
        logger.info("Check for (%s) - %s",
                    brain.getURL(), obj.other_organisations)

        if orgs:
            translated = tuple([
                org_translated[key] if key in org_translated else key
                for key in orgs
            ])
            obj.other_organisations = translated
            obj._p_changed = True
            obj.reindexObject()
            logger.info("Migrated organisations for obj (%s) - %s -> %s",
                        brain.getURL(), orgs, obj.other_organisations)

    catalog.reindexIndex(INDEX_NAME, idx_object)
    try:
        catalog.delIndex(OLD_INDEX_NAME)
        logging.info("Old index {0} was deleted".format(INDEX_NAME))
    except CatalogError:
        logging.info("Old index {0} was not found".format(INDEX_NAME))

    logger.info("Upgraded to 3.6")
