"""
This module patches the plone.app.dexterity.behaviors.metadata.IOwnership
to use the plone.app.vocabularies.Principals vocabulary for creators and
contributors.
"""
from logging import getLogger


def install_pac_metadata():
    """
    Patch the IOwnership tagged value to use the Principals vocabulary
    for creators and contributors fields.
    """
    from plone.autoform.interfaces import WIDGETS_KEY
    from plone.app.dexterity.behaviors.metadata import IOwnership

    tgv = IOwnership.getTaggedValue(WIDGETS_KEY)
    tgv["creators"].params = {"vocabulary":
                              "plone.app.vocabularies.Principals"}
    tgv["contributors"].params = {"vocabulary":
                                  "plone.app.vocabularies.Principals"}


log = getLogger(__name__)
log.info("Patched plone.app.dexterity.behaviors.metadata.IOwnership")
