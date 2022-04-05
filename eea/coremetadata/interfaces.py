"""Module where all interfaces, events and exceptions live."""

from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Int, Text, TextLine, Tuple, Datetime

try:
    from plone.app.dexterity import _
except ImportError:
    from plone.app.dexterity import PloneMessageFactory as _


class IEeaCoremetadataLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


@provider(IFormFieldProvider)
class ICoreMetadata(model.Schema):
    """ Core Metadata

    """
    title = TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
    )

    description = Text(
        title=_(u"label_description", default=u"Description"),
        description=_(
            u"help_description",
            default=u"Used in item listings and search results."
        ),
        required=True,
    )

    creation_date = Datetime(
        title=u"Publication date",
        required=False,
    )

    publication_date = Datetime(
        title=u"Creation date",
        required=False,
    )

    expiration_date = Datetime(
        title=u"Expiration date",
        required=False,
    )

    directives.widget("organisations", vocabulary="organisations_vocabulary")
    organisations = Tuple(
        title=u"Organisations",
        description=u"The responsible organisations for this item",
        required=True,
        default=(),
    )

    directives.widget("topics", vocabulary="topics_vocabulary")
    topics = Tuple(
        title=u"Topics",
        required=False,
        default=(),
        value_type=TextLine(
            title=u"Single topic",
        )
    )

    temporal_coverage = JSONField(
        title=u"Temporal coverage",
        required=False,
        widget="temporal",
        default={},
    )

    geo_coverage = JSONField(
        title=u"Geographical coverage",
        required=False,
        widget="geolocation",
        default={},
    )

    # content_type = Choice(
    #     title=u"Content Type",
    #     description=u"The item's content type",
    #     required=True,
    #     # vocabulary="portal_types_vocabulary",
    #     vocabulary="plone.app.vocabularies.PortalTypes",
    #     default="",
    # )
    #
    word_count = Int(
        title=u"Word Count",
        description=u"The item's word count",
        required=False,
        default=0,
    )

    rights = TextLine(
        title=_(u"label_title", default=u"Title"),
        description=u"Fill in copyrights",
        required=True,
        default="",
    )

    directives.widget("publisher", vocabulary="publisher_vocabulary")
    publisher = Tuple(
        title=u"Publisher",
        description=u"The responsible publisher for this item",
        required=True,
        default=(),
    )
