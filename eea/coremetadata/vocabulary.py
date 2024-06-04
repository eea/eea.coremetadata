# -*- coding: utf-8 -*-

from plone.app.vocabularies.catalog import KeywordsVocabulary as BKV
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(IVocabularyFactory)
class KeywordsVocabulary(BKV):
    def __init__(self, index):
        self.keyword_index = index


OtherOrganisationsVocabularyFactory = KeywordsVocabulary("other_organisations")
