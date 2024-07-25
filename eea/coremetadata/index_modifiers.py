from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from zope.interface import implementer


@implementer(IParsedQueryIndexModifier)
class OtherOrganisations(object):
    """
    """

    def __call__(self, value):
        return ("other_organisations", value)
