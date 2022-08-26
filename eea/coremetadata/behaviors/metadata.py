""" Custom behavior that adds core metadata fields
"""
# pylint: disable=line-too-long
import os
from plone.app.dexterity.behaviors.metadata import (DCFieldProperty,
                                                    MetadataBase)
from eea.coremetadata.metadata import ICoreMetadata
from zope.component.hooks import getSite


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


    @property
    def publisher(self):
        import pdb; pdb.set_trace()
        if not getattr(self.context, 'publisher', None):
            SITE_STRING = getSite().getId()
            publisher_env = "DEFAULT_PUBLISHER_" + SITE_STRING

            DEFAULT_PUBLISHER = os.environ.get(publisher_env, [])
            if len(DEFAULT_PUBLISHER) < 1:
                DEFAULT_PUBLISHER = os.environ.get("DEFAULT_PUBLISHER", [])

            return DEFAULT_PUBLISHER
        return self.context.publisher

    @publisher.setter
    def publisher(self, value):
        import pdb; pdb.set_trace()
        setattr(self.context, 'publisher', value)


    @property
    def other_organisations(self):
        import pdb; pdb.set_trace()
        if not getattr(self.context, 'other_organisations', None):
            SITE_STRING = getSite().getId()
            organisations_env = "DEFAULT_ORGANISATIONS_" + SITE_STRING

            DEFAULT_ORGANISATIONS = os.environ.get(organisations_env, [])
            if len(DEFAULT_ORGANISATIONS) < 1:
                DEFAULT_ORGANISATIONS = os.environ.get("DEFAULT_ORGANISATIONS", [])  # noqa

            return DEFAULT_ORGANISATIONS
        return self.context.other_organisations

    @other_organisations.setter
    def other_organisations(self, value):
        import pdb; pdb.set_trace()
        setattr(self.context, 'other_organisations', value)
