# pylint: disable=W0702
""" vocabulary.py """
from collective.taxonomy.interfaces import ITaxonomy
from zope.interface import provider  # alsoProvides,
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.CMFCore.utils import getToolByName


@provider(IVocabularyFactory)
def get_vocabulary(context, vocabulary_name):
    """get_vocabulary"""

    taxonomy = queryUtility(ITaxonomy, name=vocabulary_name)

    try:
        vocabulary = taxonomy(context)
    except:
        vocabulary = taxonomy.makeVocabulary("en")

    return vocabulary.iterEntries()


def get_catalog_values(context, index):
    """get_catalog_values"""

    catalog = getToolByName(context, "portal_catalog")

    return catalog.uniqueValuesFor(index)


@provider(IVocabularyFactory)
def organisations_vocabulary(context):
    """organisations_vocabulary"""

    vocabulary = get_vocabulary(
        context, "collective.taxonomy.eeaorganisationstaxonomy"
    )

    terms = [
        SimpleTerm(key, key, val.encode("ascii", "ignore").decode("ascii"))
        for val, key in vocabulary
    ]
    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def index_organisations_vocabulary(context):
    """index_organisations_vocabulary"""

    catalog_values = get_catalog_values(
        context, "taxonomy_eeaorganisationstaxonomy"
    )
    vocabulary = get_vocabulary(
        context, "collective.taxonomy.eeaorganisationstaxonomy"
    )
    terms = []

    for val, key in vocabulary:
        if key in catalog_values:
            terms.append(
                SimpleTerm(
                    key, key, val.encode("ascii", "ignore").decode("ascii")
                )
            )

    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def publisher_vocabulary(context):
    """publisher_vocabulary"""

    vocabulary = get_vocabulary(
        context, "collective.taxonomy.eeapublishertaxonomy"
    )

    terms = [
        SimpleTerm(key, key, val.encode("ascii", "ignore").decode("ascii"))
        for val, key in vocabulary
    ]
    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def index_publisher_vocabulary(context):
    """index_publisher_vocabulary"""

    catalog_values = get_catalog_values(
        context, "taxonomy_eeapublishertaxonomy"
    )
    vocabulary = get_vocabulary(
        context, "collective.taxonomy.eeapublishertaxonomy"
    )
    terms = []

    for val, key in vocabulary:
        if key in catalog_values:
            terms.append(
                SimpleTerm(
                    key, key, val.encode("ascii", "ignore").decode("ascii")
                )
            )

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
        vocabulary = taxonomy.makeVocabulary("en")

    terms = [
        SimpleTerm(key, key, val.encode("ascii", "ignore").decode("ascii"))
        for val, key in vocabulary.iterEntries()
    ]
    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def index_topics_vocabulary(context):
    """index_topics_vocabulary"""

    catalog_values = get_catalog_values(context, "taxonomy_eeatopicstaxonomy")
    vocabulary = get_vocabulary(
        context, "collective.taxonomy.eeatopicstaxonomy"
    )
    terms = []

    for val, key in vocabulary:
        if key in catalog_values:
            terms.append(
                SimpleTerm(
                    key, key, val.encode("ascii", "ignore").decode("ascii")
                )
            )

    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def temporal_coverage_vocabulary(context):
    """temporal_coverage_vocabulary"""

    catalog = getToolByName(context, "portal_catalog")

    terms = []

    for year in catalog.uniqueValuesFor("temporal_coverage"):
        terms.append(SimpleTerm(year, year, year))

    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def data_provenance_vocabulary(context):
    """data_provenance_vocabulary"""

    catalog = getToolByName(context, "portal_catalog")

    terms = []
    for org in catalog.uniqueValuesFor("data_provenance"):
        terms.append(SimpleTerm(org, org, org))

    terms.sort(key=lambda t: t.title)

    return SimpleVocabulary(terms)


# @implementer(IVocabularyFactory)
# class KeywordsVocabulary(BKV):
#     """KeywordsVocabulary"""
#     def __init__(self, index):
#         self.keyword_index = index
#
# TopicsVocabularyFactory = KeywordsVocabulary("topics")
