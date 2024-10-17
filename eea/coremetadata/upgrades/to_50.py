
""" Upgrade to 5.0 """
from zope.configuration.name import resolve


def to_50(context):
    """ Remove EEA Coremetadata Organisations taxonomy behavior and indexer """
    sm = context.aq_parent.getSiteManager()

    # Remove Adapter other_organisations indexer
    required = [resolve('plone.dexterity.interfaces.IDexterityContent'),
                resolve('Products.ZCatalog.interfaces.IZCatalog')]
    provided = resolve('plone.indexer.interfaces.IIndexer')
    name = 'other_organisations'
    sm.adapters.unregister(required=required, provided=provided, name=name)

    # Remove Utility other_organisations behavior
    provided = resolve('plone.behavior.interfaces.IBehavior')
    name = 'other_organisations'
    ofs_id = 'plone.behavior.interfaces.IBehavior-other_organisations'
    if ofs_id in sm.objectIds():
        sm._delObject(ofs_id, suppress_events=True)

    sm.unregisterUtility(provided=provided, name=name)
