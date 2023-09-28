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
        print ([val["value"],val["label"]])

    return data

@indexer(IContentish)
def DataProvenancenIdexer(obj):
    """Data Provenance indexer"""

    data_provenance = getattr(obj, "data_provenance", None)
    print(data_provenance)
    print("paiho")
    data = {}
    for val in obj.data_provenance['data']:
            print("val",val)
            print(val["organisation"])
            data[val["organisation"]] = val["organisation"]
            print ("ha")
     

    return data