# pylint: disable=C0412
"""Module where all interfaces, events and exceptions live."""
import os
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider, invariant, Invalid
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Int, Text, TextLine, Tuple, Datetime, Date

try:
    from plone.app.dexterity import _
except ImportError:
    from plone.app.dexterity import PloneMessageFactory as _


DEFAULT_PUBLISHER = os.environ.get("DEFAULT_PUBLISHER", [])
DEFAULT_ORGANISATIONS = os.environ.get("DEFAULT_ORGANISATIONS", [])


class EffectiveAfterExpires(Invalid):
    __doc__ = _(
    "error_invalid_publication", default=u"Invalid effective or expires date"
    )


class IEeaCoremetadataLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


@provider(IFormFieldProvider)
class ICoreMetadata(model.Schema):
    """ Core Metadata

    """
    # ownership fieldset
    model.fieldset(
        'default',
        label=_(
            'label_schema_default',
            default=u'Default'
        ),
        fields=['title', 'description', 'creation_date', 'effective',
                'expires', 'organisations', 'topics', 'temporal_coverage',
                'geo_coverage', 'word_count', 'rights', 'publisher',
                'preview_image', 'preview_caption'],
    )

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
        required=False,
    )

    creation_date = Date(
        title=_(u'label_creation_date', u'Creation Date'),
        description=_(
            u'help_creation_date',
            default=u'The date this item was created on.'),
        required=False
    )
    directives.widget('creation_date', DatetimeFieldWidget)

    effective = Datetime(
        title=_(u'label_effective_date', u'Publishing Date'),
        description=_(
            u'help_effective_date',
            default=u'If this date is in the future, the content will '
                    u'not show up in listings and searches until this date.'),
        required=False
    )
    directives.widget('effective', DatetimeFieldWidget)

    expires = Datetime(
        title=_(u'label_expiration_date', u'Expiration Date'),
        description=_(
            u'help_expiration_date',
            default=u'When this date is reached, the content will no '
                    u'longer be visible in listings and searches.'),
        required=False
    )
    directives.widget('expires', DatetimeFieldWidget)

    directives.widget("organisations", vocabulary="organisations_vocabulary")
    organisations = Tuple(
        title=_(u"Organisations"),
        description=_(u"The responsible organisations for this item"),
        required=True,
        default=tuple(DEFAULT_ORGANISATIONS),
    )

    directives.widget("topics", vocabulary="topics_vocabulary")
    topics = Tuple(
        title=_(u"Topics"),
        required=True,
        default=(),
        value_type=TextLine(
            title=u"Single topic",
        )
    )

    temporal_coverage = JSONField(
        title=_(u"Temporal coverage"),
        required=True,
        widget="temporal",
        default={},
    )

    geo_coverage = JSONField(
        title=_(u"Geographical coverage"),
        required=True,
        widget="geolocation",
        default={},
    )

    word_count = Int(
        title=_(u"Word Count"),
        description=_(u"The item's word count"),
        required=False,
        default=0,
    )

    rights = TextLine(
        title=_(u'label_copyrights', default=u'Rights'),
        description=_(
            u'help_copyrights',
            default=u'Copyright statement or other rights information on this '
                    u'item.'
        ),
        required=False,
    )

    directives.widget("publisher", vocabulary="publisher_vocabulary")
    publisher = Tuple(
        title=_(u"Publisher"),
        description=_(u"The responsible publisher for this item"),
        required=False,
        default=tuple(DEFAULT_PUBLISHER),
    )

    preview_image = NamedBlobImage(
        title=_("label_previewimage", default="Preview image"),
        description=_(
            "help_previewimage",
            default="Insert an image that will be used in listing and teaser blocks.",
        ),
        required=False,
    )

    preview_caption = TextLine(
        title=_("Preview image caption"), description="", required=False
    )

    @invariant
    def validate_start_end(data):
        if data.effective() and data.expires() and data.effective() > data.expires():
            raise EffectiveAfterExpires(
                _(
                    "error_expiration_must_be_after_effective_date",
                    default=u"Expiration date must be after publishing date.",
                )
            )
