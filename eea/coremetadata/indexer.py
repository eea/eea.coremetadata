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
def DataSourceIndexer(obj):
    """Data Source indexer"""

    data_source = getattr(obj, "data_source", None)

    if not data_source not in obj.data_source:
        return None

    data = {}
    for val in obj.data_source["organization"]:
        data[val["value"]] = val["label"]

    return data