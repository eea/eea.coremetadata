# pylint: disable=W1201
# -*- coding: utf-8 -*-
""" Upgrade to 2.1 """
import logging
from zope.i18n.interfaces import ITranslationDomain
from zope.schema.interfaces import IVocabularyFactory
from collective.taxonomy.interfaces import ITaxonomy

logger = logging.getLogger("eea.coremetadata.upgrade")


def to_20(context):
    """ Remove topics taxonomy """
    item = "collective.taxonomy.eeatopicstaxonomy"
    logger.info("Deleting taxonomy: %s" % item)

    sm = context.aq_parent.getSiteManager()
    utility = sm.queryUtility(ITaxonomy, name=item)
    utility.unregisterBehavior()

    sm.unregisterUtility(utility, ITaxonomy, name=item)
    sm.unregisterUtility(utility, IVocabularyFactory, name=item)
    sm.unregisterUtility(utility, ITranslationDomain, name=item)

    logger.info("Deleted taxonomy: %s" % item)
