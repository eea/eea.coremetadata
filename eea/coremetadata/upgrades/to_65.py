"""Upgrade to 6.5."""

from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def to_65(context):
    """Include Publication type vocabulary values in querystring responses."""
    registry = getUtility(IRegistry)
    registry["plone.app.querystring.field.publication_type.fetch_vocabulary"] = True
