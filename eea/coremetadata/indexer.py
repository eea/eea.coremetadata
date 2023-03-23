""" indexer.py """
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish


@indexer(IContentish)
def TemporalCoverageIndexer(object):
    """Temporal coverage indexer"""

    temporal_coverage = getattr(object, "temporal_coverage", None)

    if not temporal_coverage or "temporal" not in object.temporal_coverage:
        return None

    data = {}
    for val in object.temporal_coverage["temporal"]:
        data[val["value"]] = val["label"]

    return data
