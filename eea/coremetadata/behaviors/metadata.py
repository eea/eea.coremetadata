""" Custom behavior that adds core metadata fields
"""
# pylint: disable=line-too-long
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from zope.interface import implementer
from plone.app.dexterity.behaviors.metadata import (DCFieldProperty,
                                                    MetadataBase)
from eea.coremetadata.interfaces import ICoreMetadata


class CoreMetadata(MetadataBase):
    """ Core Metadata"""

    title = DCFieldProperty(ICoreMetadata["title"])

    description = DCFieldProperty(ICoreMetadata["description"])

    lineage = DCFieldProperty(ICoreMetadata["lineage"])

    original_source = DCFieldProperty(ICoreMetadata["original_source"])

    embed_url = DCFieldProperty(ICoreMetadata["embed_url"])

    webmap_url = DCFieldProperty(ICoreMetadata["webmap_url"])

    publisher = DCFieldProperty(ICoreMetadata["publisher"])

    legislative_reference = DCFieldProperty(
        ICoreMetadata["legislative_reference"])

    dpsir_type = DCFieldProperty(ICoreMetadata["dpsir_type"])

    category = DCFieldProperty(ICoreMetadata["category"])

    publication_year = DCFieldProperty(ICoreMetadata["publication_year"])

    license_copyright = DCFieldProperty(
        ICoreMetadata["license_copyright"])

    temporal_coverage = DCFieldProperty(
        ICoreMetadata["temporal_coverage"])

    geo_coverage = DCFieldProperty(ICoreMetadata["geo_coverage"])

    external_links = DCFieldProperty(ICoreMetadata["external_links"])

    data_source_info = DCFieldProperty(ICoreMetadata["data_source_info"])
