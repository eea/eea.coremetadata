# pylint: disable=W0702
""" vocabulary.py """
from collective.taxonomy.interfaces import ITaxonomy
from zope.interface import provider  # alsoProvides,
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


@provider(IVocabularyFactory)
def organisations_vocabulary(context):
    """organisations_vocabulary"""

    utility_name = "collective.taxonomy.eeaorganisationstaxonomy"
    taxonomy = queryUtility(ITaxonomy, name=utility_name)

    try:
        vocabulary = taxonomy(context)
    except:
        vocabulary = taxonomy.makeVocabulary('en')

    terms = [
        SimpleTerm(key, key, val.encode('ascii', 'ignore').decode('ascii'))
        for val, key in vocabulary.iterEntries()
    ]
    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def publisher_vocabulary(context):
    """publisher_vocabulary"""

    utility_name = "collective.taxonomy.eeapublishertaxonomy"
    taxonomy = queryUtility(ITaxonomy, name=utility_name)

    try:
        vocabulary = taxonomy(context)
    except:
        vocabulary = taxonomy.makeVocabulary('en')

    terms = [
        SimpleTerm(key, key, val.encode('ascii', 'ignore').decode('ascii'))
        for val, key in vocabulary.iterEntries()
    ]
    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def topics_vocabulary(context):
    """topics_vocabulary"""

    utility_name = "collective.taxonomy.eeatopicstaxonomy"
    taxonomy = queryUtility(ITaxonomy, name=utility_name)

    try:
        vocabulary = taxonomy(context)
    except:
        vocabulary = taxonomy.makeVocabulary('en')

    terms = [
        SimpleTerm(key, key, val.encode('ascii', 'ignore').decode('ascii'))
        for val, key in vocabulary.iterEntries()
    ]
    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)

# @implementer(IVocabularyFactory)
# class KeywordsVocabulary(BKV):
#     """KeywordsVocabulary"""
#     def __init__(self, index):
#         self.keyword_index = index
#
# TopicsVocabularyFactory = KeywordsVocabulary("topics")
