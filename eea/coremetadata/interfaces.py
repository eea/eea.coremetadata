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

    lineage = Text(
        title=u"Lineage",
        required=False,
    )

    original_source = TextLine(
        title=u"Original source",
        required=False,
    )

    embed_url = TextLine(
        title=u"Tableau URL",
        required=False,
    )

    webmap_url = TextLine(
        title=u"Embed URL",
        description=u"Webmap URL",
        required=False,
    )

    publisher = Choice(
        title=u"Organisation",
        description=u"The responsible organisation for this item",
        required=True,
        vocabulary="organisations_vocabulary",
        default="EEA",
    )

    dpsir_type = Choice(
        title=u"DPSIR", required=False, vocabulary="dpsir_vocabulary"
    )

    directives.widget("category", vocabulary="category_vocabulary")
    category = Tuple(
        title=u"Topics",
        required=False,
        default=(),
        value_type=TextLine(
            title=u"Single topic",
        ))

    legislative_reference = Tuple(
        title="Legislative reference",
        required=False,
        value_type=Choice(
            title="Single legislative reference",
            vocabulary="legislative_vocabulary",
        ))

    publication_year = Int(title=u"Publication year", required=True)

    license_copyright = TextLine(
        title=_(u"label_title", default=u"Rights"), required=False
    )

    temporal_coverage = JSONField(
        title=u"Temporal coverage",
        required=False, widget="temporal", default={}
    )

    geo_coverage = JSONField(
        title=u"Geographical coverage",
        required=False, widget="geolocation", default={}
    )

    data_source_info = RichText(
        title=u"Data source information",
        description=u"Rich text, double click for toolbar.",
        required=False,
    )

    external_links = RichText(
        title=u"External links",
        description=u"Rich text, double click for toolbar.",
        required=False,
    )
