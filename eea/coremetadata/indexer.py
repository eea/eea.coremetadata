""" indexer.py """
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish


@indexer(IContentish)
def TemporalCoverageIndexer(obj):
    """Temporal coverage indexer"""

    temporal_coverage = getattr(obj, "temporal_coverage", None)

    if not temporal_coverage or "temporal" not in obj.temporal_coverage:
        return None

    data = {}
    for val in obj.temporal_coverage["temporal"]:
        data[val["value"]] = val["label"]

    return data


@indexer(IContentish)
def DataProvenanceIdexer(obj):
    """Data Provenance indexer"""

    data_provenance = getattr(obj, "data_provenance", None)
    if not data_provenance or "data" not in obj.data_provenance:
        return None

    data = {}
    for val in obj.data_provenance['data']:
        data[val["organisation"]] = val["organisation"]

    return data
