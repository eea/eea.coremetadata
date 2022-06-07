# pylint: disable=C0412
"""Metadata schema"""
import os, six
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base
from App.special_dtml import DTMLFile
from DateTime.DateTime import DateTime
from eea.coremetadata.interfaces import ICoreMetadata as ICM
from eea.coremetadata.interfaces import ICatalogCoreMetadata, IMutableCoreMetadata
from OFS.PropertyManager import PropertyManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import WWW_DIR
from Products.CMFPlone.permissions import ModifyPortalContent
from Products.CMFPlone.permissions import View
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider, invariant, Invalid, implementer
from zope.schema import Int, Text, TextLine, Tuple, Datetime, Date, Choice
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm


try:
    from plone.app.dexterity import _
except ImportError:
    from plone.app.dexterity import PloneMessageFactory as _


DEFAULT_PUBLISHER = os.environ.get("DEFAULT_PUBLISHER", [])
DEFAULT_ORGANISATIONS = os.environ.get("DEFAULT_ORGANISATIONS", [])
_marker = []
_zone = DateTime().timezone()


def seq_strip(seq, stripper=lambda x: x.strip()):
    """ Strip a sequence of strings.
    """
    if isinstance(seq, list):
        return map(stripper, seq)

    if isinstance(seq, tuple):
        return tuple(map(stripper, seq))

    raise ValueError("%s of unsupported sequencetype %s" % (seq, type(seq)))


def tuplize(valueName, value, splitter=lambda x: x.split()):

    if isinstance(value, tuple):
        return seq_strip(value)

    if isinstance(value, list):
        return seq_strip(tuple(value))

    if isinstance(value, six.string_types):
        return seq_strip(tuple(splitter(value)))

    raise ValueError("%s of unsupported type" % valueName)


class EffectiveAfterExpires(Invalid):
    __doc__ = _(
    "error_invalid_publication", default=u"Invalid effective or expires date"
    )


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
                'preview_image', 'preview_caption', 'data_provenance'],
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

    # directives.widget('creation_date', DatetimeFieldWidget)
    creation_date = Date(
        title=_(u'label_creation_date', u'Creation Date'),
        description=_(
            u'help_creation_date',
            default=u'The date this item was created on.'),
        required=True,
    )

    directives.widget('effective', DatetimeFieldWidget)
    effective = Datetime(
        title=_(u'label_effective_date', u'Publishing Date'),
        description=_(
            u'help_effective_date',
            default=u'If this date is in the future, the content will '
                    u'not show up in listings and searches until this date.'),
        required=False,
        default=None
    )

    directives.widget('expires', DatetimeFieldWidget)
    expires = Datetime(
        title=_(u'label_expiration_date', u'Expiration Date'),
        description=_(
            u'help_expiration_date',
            default=u'When this date is reached, the content will no '
                    u'longer be visible in listings and searches.'),
        required=False,
        default=None
    )

    directives.omitted("effective", "expires")
    directives.no_omit(IEditForm, "effective", "expires")
    directives.no_omit(IAddForm, "effective", "expires")

    directives.widget("organisations", SelectFieldWidget)
    organisations = Tuple(
        title=_(u"Organisations"),
        description=_(u"The responsible organisations for this item"),
        required=True,
        value_type = Choice(vocabulary="organisations_vocabulary"),
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

    directives.widget("publisher", SelectFieldWidget)
    publisher = Tuple(
        title=_(u"Publisher"),
        description=_(u"The responsible publisher for this item"),
        value_type = Choice(vocabulary="publisher_vocabulary"),
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

    data_provenance = JSONField(
        title=_(u"Data provenance"),
        required=True,
        widget="data_provenance",
        default={},
    )

    @invariant
    def validate_start_end(data):
        if data.effective and data.expires and data.effective > data.expires:
            raise EffectiveAfterExpires(
                _(
                    "error_expiration_must_be_after_effective_date",
                    default=u"Expiration date must be after publishing date.",
                )
            )


@implementer(ICM, ICatalogCoreMetadata, IMutableCoreMetadata)
class DefaultCoreMetadataImpl(PropertyManager):

    """ Mix-in class which provides eea core metadata methods.
    """

    security = ClassSecurityInfo()

    def __init__(self, title='', subject=(), description='', contributors=(), effective_date=None, expiration_date=None, format='text/html', language='', rights=''
                 ):
        now = DateTime()
        self.creation_date = now
        self.modification_date = now
        self.creators = ()
        self._editMetadata(title, subject, description, contributors, effective_date, expiration_date, format, language, rights
                           )

    #
    #  Set-modification-date-related methods.
    #  In DefaultCoreMetadataImpl for lack of a better place.
    #

    # Class variable default for an upgrade.
    modification_date = None

    security.declarePrivate('notifyModified')

    def notifyModified(self):
        # Take appropriate action after the resource has been modified.
        # Update creators and modification_date.
        self.addCreator()
        self.setModificationDate()

    security.declareProtected(ModifyPortalContent, 'addCreator')

    def addCreator(self, creator=None):
        # Add creator to core creators.
        if creator is None:
            user = getSecurityManager().getUser()
            creator = user and user.getId()

        # call self.listCreators() to make sure self.creators exists
        if creator and not creator in self.listCreators():
            self.creators = self.creators + (creator, )

    security.declareProtected(ModifyPortalContent, 'setModificationDate')

    def setModificationDate(self, modification_date=None):
        # Set the date when the resource was last modified.
        # When called without an argument, sets the date to now.
        if modification_date is None:
            self.modification_date = DateTime()
        else:
            self.modification_date = self._datify(modification_date)

    #
    #  Core interface query methods
    #
    security.declareProtected(View, 'Title')

    def Title(self):
        # Core Title element - resource name.
        return self.title

    security.declareProtected(View, 'listCreators')

    def listCreators(self):
        # List Core Creator elements - resource authors.
        if not hasattr(aq_base(self), 'creators'):
            # for content created with CMF versions before 1.5
            owner_tuple = self.getOwnerTuple()
            if owner_tuple:
                self.creators = (owner_tuple[1],)
            else:
                self.creators = ()
        return self.creators

    security.declareProtected(View, 'Creator')

    def Creator(self):
        # Core Creator element - resource author.
        creators = self.listCreators()
        return creators and creators[0] or ''

    security.declareProtected(View, 'Subject')

    def Subject(self):
        # Core Subject element - resource keywords.
        return getattr(self, 'subject', ())  # compensate for *old* content

    security.declareProtected(View, 'Description')

    def Description(self):
        # Core Description element - resource summary.
        return self.description

    security.declareProtected(View, 'Publisher')

    def Publisher(self):
        # Core Publisher element - resource publisher.
        tool = getToolByName(self, 'portal_metadata', None)

        if tool is not None:
            return tool.getPublisher()

        return 'No publisher'

    security.declareProtected(View, 'listContributors')

    def listContributors(self):
        # Core Contributor elements - resource collaborators.
        return self.contributors

    security.declareProtected(View, 'Contributors')

    def Contributors(self):
        # Deprecated alias of listContributors.
        return self.listContributors()

    security.declareProtected(View, 'Date')

    def Date(self, zone=None):
        # Core Date element - default date.
        if zone is None:
            zone = _zone
        # Return effective_date if set, modification date otherwise
        date = getattr(self, 'effective_date', None)
        if date is None:
            date = self.modified()
        return date.toZone(zone).ISO()

    security.declareProtected(View, 'CreationDate')

    def CreationDate(self, zone=None):
        # Core Date element - date resource created.
        if zone is None:
            zone = _zone
        # return unknown if never set properly
        if self.creation_date:
            return self.creation_date.toZone(zone).ISO()
        else:
            return 'Unknown'

    security.declareProtected(View, 'EffectiveDate')

    def EffectiveDate(self, zone=None):
        # Core Date element - date resource becomes effective.
        if zone is None:
            zone = _zone
        ed = getattr(self, 'effective_date', None)
        return ed and ed.toZone(zone).ISO() or 'None'

    security.declareProtected(View, 'ExpirationDate')

    def ExpirationDate(self, zone=None):
        # Core Date element - date resource expires.
        if zone is None:
            zone = _zone
        ed = getattr(self, 'expiration_date', None)
        return ed and ed.toZone(zone).ISO() or 'None'

    security.declareProtected(View, 'ModificationDate')

    def ModificationDate(self, zone=None):
        # Core Date element - date resource last modified.
        if zone is None:
            zone = _zone
        return self.modified().toZone(zone).ISO()

    security.declareProtected(View, 'Type')

    def Type(self):
        # Core Type element - resource type.
        ti = self.getTypeInfo()
        return ti is not None and ti.Title() or 'Unknown'

    security.declareProtected(View, 'Format')

    def Format(self):
        # Core Format element - resource format.
        return self.format

    security.declareProtected(View, 'Identifier')

    def Identifier(self):
        # Core Identifier element - resource ID.
        # XXX: fixme using 'portal_metadata' (we need to prepend the
        #      right prefix to self.getPhysicalPath().
        return self.absolute_url()

    security.declareProtected(View, 'Language')

    def Language(self):
        # Core Language element - resource language.
        return self.language

    security.declareProtected(View, 'Rights')

    def Rights(self):
        # Core Rights element - resource copyright.
        return self.rights

    #
    #  Core utility methods
    #
    def content_type(self):
        """ WebDAV needs this to do the Right Thing (TM).
        """
        return self.Format()

    __FLOOR_DATE = DateTime(1970, 0)  # always effective

    security.declareProtected(View, 'isEffective')

    def isEffective(self, date):
        # Is the date within the resource's effective range?
        pastEffective = (self.effective_date is None
                         or self.effective_date <= date)
        beforeExpiration = (self.expiration_date is None
                            or self.expiration_date >= date)
        return pastEffective and beforeExpiration

    #
    #  CatalogableCore methods
    #
    security.declareProtected(View, 'created')

    def created(self):
        # Core Date element - date resource created.
        # allow for non-existent creation_date, existed always
        date = getattr(self, 'creation_date', None)
        return date is None and self.__FLOOR_DATE or date

    security.declareProtected(View, 'effective')

    def effective(self):
        # Core Date element - date resource becomes effective.
        marker = []
        date = getattr(self, 'effective_date', marker)
        if date is marker:
            date = getattr(self, 'creation_date', None)
        return date is None and self.__FLOOR_DATE or date

    __CEILING_DATE = DateTime(2500, 0)  # never expires

    security.declareProtected(View, 'expires')

    def expires(self):
        # Core Date element - date resource expires.
        date = getattr(self, 'expiration_date', None)
        return date is None and self.__CEILING_DATE or date

    security.declareProtected(View, 'modified')

    def modified(self):
        # Core Date element - date resource last modified.
        date = self.modification_date
        if date is None:
            # Upgrade.
            date = DateTime(self._p_mtime)
            self.modification_date = date
        return date

    security.declareProtected(View, 'getMetadataHeaders')

    def getMetadataHeaders(self):
        # Return RFC-822-style headers.
        hdrlist = []
        hdrlist.append(('Title', self.Title()))
        hdrlist.append(('Subject', ', '.join(self.Subject())))
        hdrlist.append(('Publisher', self.Publisher()))
        hdrlist.append(('Description', self.Description()))
        hdrlist.append(('Contributors', '; '.join(self.Contributors())))
        hdrlist.append(('Effective_date', self.EffectiveDate()))
        hdrlist.append(('Expiration_date', self.ExpirationDate()))
        hdrlist.append(('Type', self.Type()))
        hdrlist.append(('Format', self.Format()))
        hdrlist.append(('Language', self.Language()))
        hdrlist.append(('Rights', self.Rights()))
        return hdrlist

    #
    #  MutableCore methods
    #
    security.declarePrivate('_datify')

    def _datify(self, attrib):
        if attrib == 'None':
            attrib = None
        elif not isinstance(attrib, DateTime):
            if attrib is not None:
                attrib = DateTime(attrib)
        return attrib

    security.declareProtected(ModifyPortalContent, 'setTitle')

    def setTitle(self, title):
        # Set Core Title element - resource name.
        self.title = title

    security.declareProtected(ModifyPortalContent, 'setCreators')

    def setCreators(self, creators):
        # Set Core Creator elements - resource authors.
        self.creators = tuplize('creators', creators)

    security.declareProtected(ModifyPortalContent, 'setSubject')

    def setSubject(self, subject):
        # Set Core Subject element - resource keywords.
        self.subject = tuplize('subject', subject)

    security.declareProtected(ModifyPortalContent, 'setDescription')

    def setDescription(self, description):
        # Set Core Description element - resource summary.
        self.description = description

    security.declareProtected(ModifyPortalContent, 'setContributors')

    def setContributors(self, contributors):
        # Set Core Contributor elements - resource collaborators.
        semi_split = lambda s: map(lambda x: x.strip(), s.split(';'))
        self.contributors = tuplize('contributors', contributors, semi_split)

    security.declareProtected(ModifyPortalContent, 'setEffectiveDate')

    def setEffectiveDate(self, effective_date):
        # Set Core Date element - date resource becomes effective.
        self.effective_date = self._datify(effective_date)

    security.declareProtected(ModifyPortalContent, 'setExpirationDate')

    def setExpirationDate(self, expiration_date):
        # Set Core Date element - date resource expires.
        self.expiration_date = self._datify(expiration_date)

    security.declareProtected(ModifyPortalContent, 'setFormat')

    def setFormat(self, format):
        # Set Core Format element - resource format.
        self.format = format

    security.declareProtected(ModifyPortalContent, 'setLanguage')

    def setLanguage(self, language):
        # Set Core Language element - resource language.
        self.language = language

    security.declareProtected(ModifyPortalContent, 'setRights')

    def setRights(self, rights):
        # Set Core Rights element - resource copyright.
        self.rights = rights

    #
    #  Management tab methods
    #

    security.declarePrivate('_editMetadata')

    def _editMetadata(self, title=_marker, subject=_marker, description=_marker, contributors=_marker, effective_date=_marker, expiration_date=_marker, format=_marker, language=_marker, rights=_marker
                      ):
        # Update the editable metadata for this resource.
        if title is not _marker:
            self.setTitle(title)
        if subject is not _marker:
            self.setSubject(subject)
        if description is not _marker:
            self.setDescription(description)
        if contributors is not _marker:
            self.setContributors(contributors)
        if effective_date is not _marker:
            self.setEffectiveDate(effective_date)
        if expiration_date is not _marker:
            self.setExpirationDate(expiration_date)
        if format is not _marker:
            self.setFormat(format)
        if language is not _marker:
            self.setLanguage(language)
        if rights is not _marker:
            self.setRights(rights)

    security.declareProtected(ModifyPortalContent, 'manage_metadata')
    manage_metadata = DTMLFile('zmi_metadata', WWW_DIR)

    security.declareProtected(ModifyPortalContent, 'manage_editMetadata')

    def manage_editMetadata(self, title, subject, description, contributors, effective_date, expiration_date, format, language, rights, REQUEST
                            ):
        """ Update metadata from the ZMI.
        """
        self._editMetadata(title, subject, description, contributors, effective_date, expiration_date, format, language, rights
                           )
        REQUEST['RESPONSE'].redirect(self.absolute_url()
                                     + '/manage_metadata'
                                     + '?manage_tabs_message=Metadata+updated.')

    security.declareProtected(ModifyPortalContent, 'editMetadata')

    def editMetadata(self, title='', subject=(), description='', contributors=(), effective_date=None, expiration_date=None, format='text/html', language='en-US', rights=''
                     ):
        # Need to add check for webDAV locked resource for TTW methods.
        # As per bug #69, we can't assume they use the webdav
        # locking interface, and fail gracefully if they don't.
        if hasattr(self, 'failIfLocked'):
            self.failIfLocked()

        self._editMetadata(title=title, subject=subject, description=description, contributors=contributors, effective_date=effective_date, expiration_date=expiration_date, format=format, language=language, rights=rights
                           )
        self.reindexObject()

InitializeClass(DefaultCoreMetadataImpl)
