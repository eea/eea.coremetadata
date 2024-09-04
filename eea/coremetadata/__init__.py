"""Main product initializer"""

from .patches import install_patches
from zope.i18nmessageid.message import MessageFactory

EEAMessageFactory = MessageFactory("eea")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    install_patches()
