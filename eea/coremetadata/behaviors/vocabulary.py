""" vocabulary.py """
from plone.app.vocabularies.catalog import KeywordsVocabulary as BKV
from zope.interface import implementer, provider  # alsoProvides,
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


def values_to_vocab(values):
    """ values_to_vocab """
    terms = [SimpleTerm(x, x, x) for x in values]
    terms.sort(key=lambda t: t.title)
    vocab = SimpleVocabulary(terms)

    return vocab


organisations = {
    "EEA": dict(
        title="European Environment Agency",
        website="https://www.eea.europa.eu/"
    ),
    "DG ENV": dict(
        title="Environment Directorate General of the European Commission ",
        website="https://ec.europa.eu/environment/index_en.htm",
    ),
    "ETC/ICM": dict(
        title="European Topic Centre on Inland, Coastal and Marine waters",
        website="https://www.eionet.europa.eu/etcs/etc-icm",
    ),
    "OSPAR": dict(
        title="OSPAR Commission-Protecting and conserving the "
        "North-East Atlantic and its resources",
        website="https://www.ospar.org/",
    ),
    "HELCOM": dict(
        title="The Baltic Marine Environment Protection Commission",
        website="https://helcom.fi/",
    ),
    "UNEP/MAP": dict(
        title="UN Environment Programme / Mediterranean Action Plan",
        website="www.unepmap.org",
    ),
    "BSC": dict(
        title="Black Sea Commission (BSC)",
        website="http://www.blacksea-commission.org/",
    ),
    "Other": dict(title="Other", website=""),
}


@provider(IVocabularyFactory)
def organisations_vocabulary(context):
    """organisations_vocabulary"""
    terms = [
        SimpleTerm(acro, acro, info["title"])
        for acro, info in organisations.items()
    ]
    terms.sort(key=lambda t: t.title)
    vocab = SimpleVocabulary(terms)
    return vocab


@implementer(IVocabularyFactory)
class KeywordsVocabulary(BKV):
    """KeywordsVocabulary"""
    def __init__(self, index):
        self.keyword_index = index

TopicsVocabularyFactory = KeywordsVocabulary("topics")
