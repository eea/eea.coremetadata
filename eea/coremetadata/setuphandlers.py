"""Custom setup"""

from plone.registry import Record
from plone.registry import field
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from zope.component import getUtility
from zope.interface import implementer


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


def post_install(context):
    """Post install script"""
    configure_publication_type_querystring()


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
