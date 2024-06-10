"""vocabularies"""
from plone.app.vocabularies.catalog import KeywordsVocabulary as BKV
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(IVocabularyFactory)
class OtherOrganisationKeywords(BKV):
    """Core metada other organisation keywords"""

    def __init__(self, index):
        self.keyword_index = index


OtherOrganisationsVocabularyFactory = OtherOrganisationKeywords(
    "other_organisations")
