""" Custom behavior that adds core metadata fields
"""
# pylint: disable=line-too-long
from plone.app.dexterity.behaviors.metadata import (DCFieldProperty,
                                                    MetadataBase)
from eea.coremetadata.interfaces import ICoreMetadata


class CoreMetadata(MetadataBase):
    """ Core Metadata"""

    title = DCFieldProperty(ICoreMetadata["title"])

    description = DCFieldProperty(ICoreMetadata["description"])

    organisation = DCFieldProperty(ICoreMetadata["organisation"])

    topics = DCFieldProperty(ICoreMetadata["topics"])

    publication_year = DCFieldProperty(ICoreMetadata["publication_year"])

    temporal_coverage = DCFieldProperty(
        ICoreMetadata["temporal_coverage"])

    geo_coverage = DCFieldProperty(ICoreMetadata["geo_coverage"])
