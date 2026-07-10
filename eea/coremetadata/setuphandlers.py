"""Custom setup"""

import logging

from plone import api
from plone.dexterity.fti import DexterityFTIModificationDescription
from plone.registry import Record
from plone.registry import field
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from zope.component import getUtility
from zope.interface import implementer
from zope.lifecycleevent import modified


logger = logging.getLogger(__name__)

PUBLICATION_CONTENT_TYPES = ("briefing", "report_pdf", "web_report")
PUBLICATION_TYPE_BEHAVIOR = (
    "collective.taxonomy.generated.eeapublicationtypetaxonomy"
)


PUBLICATION_TYPE_QUERYSTRING_PREFIX = (
    "plone.app.querystring.field.taxonomy_eeapublicationtypetaxonomy"
)


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Hidden profiles"""

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "eea.coremetadata:uninstall",
        ]


def configure_publication_type_querystring():
    """Configure Publication type search filter after taxonomy import."""

    registry = getUtility(IRegistry)
    prefix = PUBLICATION_TYPE_QUERYSTRING_PREFIX

    registry.records[prefix + ".title"] = Record(field.TextLine(), "Publication type")
    registry.records[prefix + ".description"] = Record(field.Text(), "")
    registry.records[prefix + ".enabled"] = Record(field.Bool(), True)
    registry.records[prefix + ".sortable"] = Record(field.Bool(), True)
    registry.records[prefix + ".operations"] = Record(
        field.List(value_type=field.TextLine()),
        ["plone.app.querystring.operation.selection.is"],
    )
    registry.records[prefix + ".group"] = Record(field.TextLine(), "Taxonomy")
    registry.records[prefix + ".vocabulary"] = Record(
        field.TextLine(), "index_publication_type_vocabulary"
    )
    registry.records[prefix + ".fetch_vocabulary"] = Record(field.Bool(), False)


def enable_publication_type_behavior(portal=None):
    """Enable the generated taxonomy behavior on publication content types."""

    portal = portal or api.portal.get()
    portal_types = portal["portal_types"]
    enabled = []

    for portal_type in PUBLICATION_CONTENT_TYPES:
        fti = portal_types.get(portal_type)
        if fti is None:
            logger.warning(
                "Cannot enable Publication type behavior: %s FTI is missing",
                portal_type,
            )
            continue

        behaviors = list(fti.behaviors or ())
        if PUBLICATION_TYPE_BEHAVIOR in behaviors:
            continue

        behaviors.append(PUBLICATION_TYPE_BEHAVIOR)
        fti.behaviors = tuple(behaviors)
        modified(
            fti,
            DexterityFTIModificationDescription("behaviors", ""),
        )
        enabled.append(portal_type)
        logger.info(
            "Enabled Publication type behavior on %s",
            portal_type,
        )

    return enabled


def post_install(context):
    """Post install script"""
    configure_publication_type_querystring()
    enable_publication_type_behavior(context.aq_parent)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
