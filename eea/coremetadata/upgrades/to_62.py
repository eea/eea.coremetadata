"""Upgrade to 6.2."""

from eea.coremetadata.upgrades.to_61 import upgrade_publication_type


def to_62(context):
    """Complete Publication type setup if profile 6.1 already ran."""

    upgrade_publication_type(context)
