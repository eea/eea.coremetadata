# pylint: disable=W0622
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IEeaCoremetadataLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IMinimalCoreMetadata(Interface):

    """ Minimal set of eea core metadata elements.
    """
    __module__ = 'eea.coremetadata.interfaces'

    def Title():
        """ Return a single string, the DCMI Title element (resource name).
        o Permission:  View
        """

    def Description():
        """ Return the DCMI Description element (resource summary).
        o Result is a natural language description of this object.
        o Permission:  View
        """

    def Type():
        """ Return the DCMI Type element (resource type).
        o Result a human-readable type name for the resource (typically
          the Title of its type info object).
        o Permission:  View
        """


class ICoreMetadata(IMinimalCoreMetadata):
    """ Core metadata
    """
    __module__ = 'eea.coremetadata.interfaces'

    def listCreators():
        """ Return a sequence of DCMI Creator elements (resource authors).
        o Depending on the implementation, this returns the full name(s) of the
          author(s) of the content object or their ids.
        o Permission:  View
        """

    def Creator():
        """ Return the first DCMI Creator element, or an empty string.
        o Permission:  View
        """

    def Subject():
        """ Return a sequence of DCMI Subject elements (resource keywords).
        o Result is zero or more keywords associated with the content object.
        o Permission:  View
        """

    def Publisher():
        """ Return the DCMI Publisher element (resource publisher).
        o Result is the full formal name of the entity or person responsible
          for publishing the resource.
        o Permission:  View
        """

    def listContributors():
        """ Return a sequence of DCMI Contributor elements (resource
            collaborators).
        o Return zero or more collaborators (beyond thos returned by
          'listCreators').
        o Permission:  View
        """

    def Contributors():
        """ Deprecated alias for 'listContributors'.
        o 'initial caps' names are reserved for strings.
        """

    def Date(zone=None):
        """ Return the DCMI Date element (default resource date).
        o Result is a string, formatted 'YYYY-MM-DD H24:MN:SS TZ'.
        o If 'zone' is 'None', return the time in the system default
          timezone.
        o Permission:  View
        """

    def CreationDate(zone=None):
        """ Return the DCMI Date element (date resource created).
        o Result is a string, formatted 'YYYY-MM-DD H24:MN:SS TZ'.
        o If 'zone' is 'None', return the time in the system default
          timezone.
        o Permission:  View
        """

    def EffectiveDate(zone=None):
        """ Return the DCMI Date element (date resource becomes effective).
        o Result is a string, formatted 'YYYY-MM-DD H24:MN:SS TZ', or
          None.
        o If 'zone' is 'None', return the time in the system default
          timezone.
        o Permission:  View
        """

    def ExpirationDate(zone=None):
        """ Return the DCMI Date element (date resource expires).
        o Result is a string, formatted 'YYYY-MM-DD H24:MN:SS TZ', or
          None.
        o If 'zone' is 'None', return the time in the system default
          timezone.
        o Permission:  View
        """

    def ModificationDate(zone=None):
        """ DCMI Date element - date resource last modified.
        o Result is a string, formatted 'YYYY-MM-DD H24:MN:SS TZ'.
        o If 'zone' is 'None', return the time in the system default
          timezone.
        o Permission:  View
        """

    def Format():
        """ Return the DCMI Format element (resource format).
        o Result is the resource's MIME type (e.g. 'text/html',
          'image/png', etc.).
        o Permission:  View
        """

    def Identifier():
        """ Return the DCMI Identifier element (resource ID).
        o Result is a unique ID (a URL) for the resource.
        o Permission:  View
        """

    def Language():
        """ DCMI Language element (resource language).
        o Result it the RFC language code (e.g. 'en-US', 'pt-BR') for the
          resource.
        o Permission:  View
        """

    def Rights():
        """ Return the DCMI Rights element (resource copyright).
        o Return a string describing the intellectual property status, if
          any, of the resource.
        o Permission:  View
        """


class ICatalogCoreMetadata(Interface):
    """ Provide Zope-internal date attributes for cataloging purposes.
    """

    __module__ = 'eea.coremetadata.interfaces'

    def created():
        """ Return the DateTime form of CreationDate.
        o Permission:  View
        """

    def effective():
        """ Return the DateTime form of EffectiveDate.
        o Permission:  View
        """

    def expires():
        """ Return the DateTime form of ExpirationDate.
        o Permission:  View
        """

    def modified():
        """ Return the DateTime form of ModificationDate
        o Permission:  View
        """


class IMutableMinimalCoreMetadata(IMinimalCoreMetadata):

    """ Update interface for minimal set of mutable metadata.
    """
    __module__ = 'eea.coremetadata.interfaces'

    def setTitle(title):
        """ Set DCMI Title element - resource name.
        o Permission:  Modify portal content
        """

    def setDescription(description):
        """ Set DCMI Description element - resource summary.
        o Permission:  Modify portal content
        """


class IMutableCoreMetadata(IMutableMinimalCoreMetadata, ICoreMetadata):

    """ Update interface for mutable metadata.
    """

    __module__ = 'eea.coremetadata.interfaces'

    def setCreators(creators):
        """ Set DCMI Creator elements - resource authors.
        o Permission:  Modify portal content
        """

    def setSubject(subject):
        """ Set DCMI Subject element - resource keywords.
        o Permission:  Modify portal content
        """

    def setContributors(contributors):
        """ Set DCMI Contributor elements - resource collaborators.
        o Permission:  Modify portal content
        """

    def setEffectiveDate(effective_date):
        """ Set DCMI Date element - date resource becomes effective.
        o Permission:  Modify portal content
        """

    def setExpirationDate(expiration_date):
        """ Set DCMI Date element - date resource expires.
        o Permission:  Modify portal content
        """

    def setFormat(format):
        """ Set DCMI Format element - resource format.
        o Permission:  Modify portal content
        """

    def setLanguage(language):
        """ Set DCMI Language element - resource language.
        o Permission:  Modify portal content
        """

    def setRights(rights):
        """ Set DCMI Rights element - resource copyright.
        o Permission:  Modify portal content
        """
