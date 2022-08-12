""" Custom setup
"""
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from eea.coremetadata.utils import BlocksTraverser, \
    TemporalBlockTransformer, GeoBlockTransformer, \
    fix_temporal_coverage, fix_geographic_coverage


logger = logging.getLogger('eea.coremetadata.installation')


@implementer(INonInstallable)
class HiddenProfiles(object):
    """ Hidden profiles
    """

    def getNonInstallableProfiles(self):
        """ Hide uninstall profile from site-creation and quickinstaller.
        """
        return [
            'eea.coremetadata:uninstall',
        ]


def post_install(context):
    """ Post install script
    """
    # Do something at the end of the installation of this package.
    import pdb; pdb.set_trace()


def uninstall(context):
    """ Uninstall script
    """
    # Do something at the end of the uninstallation of this package.
