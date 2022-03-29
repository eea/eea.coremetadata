"""Module where all interfaces, events and exceptions live."""

from plone.app.dexterity import _
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Choice, Int, Text, TextLine, Tuple


class IEeaCoremetadataLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


@provider(IFormFieldProvider)
class ICoreMetadata(model.Schema):
    """ Core Metadata

    """
    title = TextLine(title=_(u"label_title", default=u"Title"), required=True)

    description = Text(
        title=_(u"label_description", default=u"Description"),
        description=_(
            u"help_description",
            default=u"Used in item listings and search results."
        ),
        required=True,
    )

    creation_date = Int(title=u"Publication date", required=True)
    publication_date = Int(title=u"Creation date", required=True)
    expiration_date = Int(title=u"Expiration date", required=True)

    organisation = Choice(
        title=u"Organisation",
        description=u"The responsible organisation for this item",
        required=True,
        vocabulary="organisations_vocabulary",
        default="EEA",
    )

    directives.widget("topics", vocabulary="topics_vocabulary")
    topics = Tuple(
        title=u"Topics",
        required=False,
        default=(),
        value_type=TextLine(
            title=u"Single topic",
        ))

    temporal_coverage = JSONField(
        title=u"Temporal coverage",
        required=False, widget="temporal", default={}
    )

    geo_coverage = JSONField(
        title=u"Geographical coverage",
        required=False, widget="geolocation", default={}
    )
