"""Upgrade to 6.1."""

import logging

from eea.coremetadata.setuphandlers import configure_publication_type_querystring
from eea.coremetadata.setuphandlers import enable_publication_type_behavior
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger("eea.coremetadata.upgrade")

INDEX_NAME = "taxonomy_eeapublicationtypetaxonomy"


def to_61(context):
    """Install Publication type on sites upgrading from profile 5.1."""

    configure_publication_type_querystring()

    portal = context.aq_parent
    enable_publication_type_behavior(portal)
    catalog = getToolByName(portal, "portal_catalog")

    if INDEX_NAME in catalog.indexes():
        catalog.reindexIndex(INDEX_NAME, None)
        logger.info("Reindexed %s", INDEX_NAME)
