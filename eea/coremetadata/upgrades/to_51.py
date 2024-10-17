
""" Upgrade to 5.1 """
from plone.dexterity.interfaces import IDexterityFTI
from plone import api
from zope.component import queryUtility


def to_51(context):
    """Disable EEA Coremetadata Organisations behavior on all content types"""

    portal_types = api.portal.get_tool(name='portal_types')
    for fti_id in portal_types.objectIds():
        fti = queryUtility(IDexterityFTI, name=fti_id)

        if fti and 'other_organisations' in fti.behaviors:
            fti.behaviors = [
                b for b in fti.behaviors if b != 'other_organisations']
