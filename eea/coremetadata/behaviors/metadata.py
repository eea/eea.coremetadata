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

    organisations = DCFieldProperty(ICoreMetadata["organisations"])

    topics = DCFieldProperty(ICoreMetadata["topics"])

    # creation_date = DCFieldProperty(ICoreMetadata["creation_date"])
    effective_date = DCFieldProperty(ICoreMetadata["effective_date"])
    expires_date = DCFieldProperty(ICoreMetadata["expires_date"])

    temporal_coverage = DCFieldProperty(
        ICoreMetadata["temporal_coverage"])

    geo_coverage = DCFieldProperty(ICoreMetadata["geo_coverage"])

    # content_type = DCFieldProperty(ICoreMetadata["content_type"])

    word_count = DCFieldProperty(ICoreMetadata["word_count"])

    rights = DCFieldProperty(ICoreMetadata["rights"])

    publisher = DCFieldProperty(ICoreMetadata["publisher"])
