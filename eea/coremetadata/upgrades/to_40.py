# pylint: disable=W1201, C0301, C0111, W0640, W1202
# -*- coding: utf-8 -*-
""" Upgrade to 4.0 """
import logging

from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import iterSchemataForType
from plone import api
from Acquisition import aq_self
from eea.coremetadata.metadata import ICoreMetadata

logger = logging.getLogger("eea.coremetadata.upgrade")

INDEX_NAME = "other_organisations"


def to_40(context):
    catalog = getToolByName(context.aq_parent, "portal_catalog")

    idx_object = catalog.Indexes[INDEX_NAME]

    types = getToolByName(context, 'portal_types').listTypeInfo()
    migrated_types = []

    for _type in types:
        portal_type = _type.getId()
        for schemata in iterSchemataForType(portal_type):
            if schemata is ICoreMetadata:
                migrated_types.append(portal_type)

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

        if orgs is None:
            obj.other_organisations = tuple()
            obj._p_changed = True
            obj.reindexObject()
            logger.info("Updated other organisations (%s) - empty",
                        brain.getURL())
        elif isinstance(orgs, tuple):
            orgs_clean = tuple([term for term in orgs if len(term.strip())])
            if orgs_clean and orgs != orgs_clean:
                obj.other_organisations = orgs_clean
                obj._p_changed = True
                obj.reindexObject()
                logger.info("Updated other organisations (%s) - %s -> %s",
                            brain.getURL(), orgs, obj.other_organisations)

    catalog.reindexIndex(INDEX_NAME, idx_object)

    logger.info("Upgraded to 4.0")
