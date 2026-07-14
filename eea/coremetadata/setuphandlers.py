"""Custom setup"""

import logging

from plone import api
from plone.behavior.interfaces import IBehavior
from plone.dexterity.fti import DexterityFTIModificationDescription
from plone.registry import Record
from plone.registry import field
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer
from zope.lifecycleevent import modified


logger = logging.getLogger(__name__)

PUBLICATION_CONTENT_TYPES = ("briefing", "report_pdf", "web_report")
PUBLICATION_TYPE_BEHAVIOR = "eea.coremetadata.publication_type"
GENERATED_PUBLICATION_TYPE_BEHAVIOR = (
    "collective.taxonomy.generated.eeapublicationtypetaxonomy"
)
GENERATED_PUBLICATION_TYPE_FIELD = "taxonomy_eeapublicationtypetaxonomy"


PUBLICATION_TYPE_QUERYSTRING_PREFIX = "plone.app.querystring.field.publication_type"


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
    """Enable the dedicated behavior on publication content types."""

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

        behaviors = [
            behavior
            for behavior in (fti.behaviors or ())
            if behavior != GENERATED_PUBLICATION_TYPE_BEHAVIOR
        ]
        if PUBLICATION_TYPE_BEHAVIOR not in behaviors:
            behaviors.append(PUBLICATION_TYPE_BEHAVIOR)
            enabled.append(portal_type)

        if tuple(behaviors) == tuple(fti.behaviors or ()):
            continue

        fti.behaviors = tuple(behaviors)
        modified(
            fti,
            DexterityFTIModificationDescription("behaviors", ""),
        )
        logger.info(
            "Enabled Publication type behavior on %s",
            portal_type,
        )

    return enabled


def disable_generated_publication_type(portal=None):
    """Remove the generated behavior and its search configuration."""

    portal = portal or api.portal.get()
    for fti in portal["portal_types"].objectValues():
        behaviors = getattr(fti, "behaviors", None)
        if not behaviors or GENERATED_PUBLICATION_TYPE_BEHAVIOR not in behaviors:
            continue

        fti.behaviors = tuple(
            behavior
            for behavior in behaviors
            if behavior != GENERATED_PUBLICATION_TYPE_BEHAVIOR
        )
        modified(
            fti,
            DexterityFTIModificationDescription("behaviors", ""),
        )
        logger.info(
            "Disabled generated Publication type behavior on %s",
            fti.getId(),
        )

    behavior = queryUtility(IBehavior, name=GENERATED_PUBLICATION_TYPE_BEHAVIOR)
    if behavior is not None:
        behavior.removeIndex()
        behavior.deactivateSearchable()

    catalog = portal["portal_catalog"]
    if GENERATED_PUBLICATION_TYPE_FIELD in catalog.schema():
        catalog.delColumn(GENERATED_PUBLICATION_TYPE_FIELD)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
