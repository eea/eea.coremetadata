"""Upgrade to 6.2."""

import logging

from eea.coremetadata.setuphandlers import configure_publication_type_querystring
from eea.coremetadata.setuphandlers import disable_generated_publication_type
from eea.coremetadata.setuphandlers import enable_publication_type_behavior
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger("eea.coremetadata.upgrade")

INDEX_NAME = "publication_type"


def to_62(context):
    """Replace the generated taxonomy field with the dedicated behavior."""

    configure_publication_type_querystring()

    portal = context.aq_parent
    disable_generated_publication_type(portal)
    enable_publication_type_behavior(portal)
    catalog = getToolByName(portal, "portal_catalog")

    if INDEX_NAME in catalog.indexes():
        catalog.reindexIndex(INDEX_NAME, None)
        logger.info("Reindexed %s", INDEX_NAME)
