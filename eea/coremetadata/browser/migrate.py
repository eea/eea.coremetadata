from Products.Five.browser import BrowserView
from plone import api
from eea.coremetadata.behaviors.vocabulary import get_vocabulary
import logging


from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI

class OtherOrganisation(BrowserView):
    """ see #261751 """

    def __call__(self):
        logger = logging.getLogger("export")
        typeList = getToolByName(self.context, 'portal_types').listTypeInfo()
        for aType in typeList:
            logger.info(aType.__name__+"-------------------")
            logger.info(getattr(aType, 'ICoreMetadata', None))
            logger.info(getattr(aType, 'CoreMetadata', None))
            self.get_fields(aType)

        vocabulary = get_vocabulary(self.context, "collective.taxonomy.eeaorganisationstaxonomy")
        dict_other_organisations = {key:val  for val, key in vocabulary}
        self.migrate_portal_type('my_data')

        # brains = api.content.find(context=self.context, portal_type='mydata')
        # for brain in brains:
        #     object = brain.getObject()
        #     pdb.set_trace()
        #     object.other_organisations2 = [dict_other_organisations[key] for key in object.other_organisations if key in dict_other_organisations]
        #     # object._p_changed = True

        return "Done"

    def migrate_portal_type(self, portal_type_name):
        brains = api.content.find(context=self.context, portal_type=portal_type_name)
        for brain in brains:
            object = brain.getObject()
            import pdb; pdb.set_trace()
            pdb.set_trace()
            object.other_organisations2 = [dict_other_organisations[key] for key in object.other_organisations if key in dict_other_organisations]

    #### DELETE BELOW
    def get_fields(self, portal_type):
        fti = getUtility(IDexterityFTI, name=portal_type.__name__)
        schema = fti.lookupSchema()
        fields = schema.names()
        for bname in fti.behaviors:
            factory = getUtility(IBehavior, bname)
            behavior = factory.interface
            fields += behavior.names()
        import pdb; pdb.set_trace()

        return fields    