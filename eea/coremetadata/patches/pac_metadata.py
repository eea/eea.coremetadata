from logging import getLogger


def install_pac_metadata():
    from plone.autoform.interfaces import WIDGETS_KEY
    from plone.app.dexterity.behaviors.metadata import IOwnership

    tgv = IOwnership.getTaggedValue(WIDGETS_KEY)
    tgv["creators"].params = {"vocabulary": "plone.app.vocabularies.Principals"}
    tgv["contributors"].params = {"vocabulary": "plone.app.vocabularies.Principals"}


log = getLogger(__name__)
log.info("Patched plone.app.dexterity.behaviors.metadata.IOwnership")
