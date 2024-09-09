"""Main product initializer"""

from zope.i18nmessageid.message import MessageFactory
from .patches import install_patches


EEAMessageFactory = MessageFactory("eea")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    install_patches()
