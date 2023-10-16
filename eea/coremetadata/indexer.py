""" indexer.py """
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish


@indexer(IContentish)
def temporal_coverage_indexer(obj):
    """Temporal coverage indexer"""

    temporal_coverage = getattr(obj, "temporal_coverage", None)

    if not temporal_coverage or "temporal" not in obj.temporal_coverage:
        return None

    data = {}
    for val in obj.temporal_coverage["temporal"]:
        data[val["value"]] = val["label"]

    return data


@indexer(IContentish)
def data_provenance_indexer(obj):
    """Data Provenance indexer"""

    data_provenance = getattr(obj, "data_provenance", {})
    if not data_provenance or "data" not in data_provenance:
        return None

    data = {}
    for val in data_provenance.get('data', []):
        organisation = val.get("organisation", "")
        if organisation:
            data[organisation] = organisation
    return data
