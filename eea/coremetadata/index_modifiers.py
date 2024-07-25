"""Modify indexer."""

from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from zope.interface import implementer


@implementer(IParsedQueryIndexModifier)
class OtherOrganisations(object):
    """ Get other_organisation index instead taxonomy_eeaorganisationstaxonomy
    """

    def __call__(self, value):
        """
        """
        return ("other_organisations", value)
