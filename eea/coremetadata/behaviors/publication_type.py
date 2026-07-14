"""Publication type behavior."""

from plone.app.dexterity import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import provider
from zope.schema import Choice


@provider(IFormFieldProvider)
class IPublicationType(model.Schema):
    """Add a managed publication type to publication content."""

    publication_type = Choice(
        title=_("Publication type"),
        description=_("Select the publication type."),
        required=True,
        vocabulary="publication_type_vocabulary",
    )
