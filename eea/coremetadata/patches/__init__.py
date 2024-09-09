"""
This module initializes and installs patches for the eea.coremetadata package.
It provides functionality to apply custom patches to Plone's core behavior.
"""

from .pac_metadata import install_pac_metadata


def install_patches():
    """
    Install all patches defined in the eea.coremetadata package.
    This function should be called during the package initialization
    to ensure all custom patches are applied.
    """
    install_pac_metadata()
