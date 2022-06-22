""" Custom behavior that adds core metadata fields
"""
# pylint: disable=line-too-long
from plone.app.dexterity.behaviors.metadata import (DCFieldProperty,
                                                    MetadataBase)
from eea.coremetadata.metadata import ICoreMetadata


class CoreMetadata(MetadataBase):
    """ Core Metadata"""

    title = DCFieldProperty(ICoreMetadata["title"])

    description = DCFieldProperty(ICoreMetadata["description"])

    other_organisations = DCFieldProperty(ICoreMetadata["other_organisations"])

    topics = DCFieldProperty(ICoreMetadata["topics"])

    effective = DCFieldProperty(ICoreMetadata["effective"],
                                get_name="effective_date")
    expires = DCFieldProperty(ICoreMetadata["expires"],
                              get_name="expiration_date")

    temporal_coverage = DCFieldProperty(
        ICoreMetadata["temporal_coverage"])

    geo_coverage = DCFieldProperty(ICoreMetadata["geo_coverage"])

    rights = DCFieldProperty(ICoreMetadata["rights"])

    publisher = DCFieldProperty(ICoreMetadata["publisher"])

    preview_image = DCFieldProperty(ICoreMetadata["preview_image"])
    preview_caption = DCFieldProperty(ICoreMetadata["preview_caption"])

    data_provenance = DCFieldProperty(ICoreMetadata["data_provenance"])
