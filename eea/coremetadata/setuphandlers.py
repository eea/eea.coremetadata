# pylint: disable=C0301,W1201,C1801
""" Custom setup
"""
import logging
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from eea.coremetadata.utils import BlocksTraverser, \
    TemporalBlockTransformer, GeoBlockTransformer, \
    fix_temporal_coverage, fix_geographic_coverage, fix_data_provenance


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
    # migrate geo/dataprovenance/temporal data
    catalog = context.aq_parent.portal_catalog
    brains = catalog(_nonsense=True)

    count = 0
    logger.info("Got %s brains" % len(brains))
    for brain in brains:
        obj = brain.getObject()
        changed = False

        if hasattr(obj.aq_inner.aq_self, 'blocks') and \
                hasattr(obj.aq_inner.aq_self, 'blocks_layout'):

            traverser = BlocksTraverser(obj)

            temporal_fixer = TemporalBlockTransformer(obj)
            geolocation_fixer = GeoBlockTransformer(obj)

            traverser(temporal_fixer)
            traverser(geolocation_fixer)

        if hasattr(obj, 'temporal_coverage'):
            if len(obj.temporal_coverage) > 0:
                temp_cov = obj.temporal_coverage['temporal']

                obj.temporal_coverage['temporal'] = fix_temporal_coverage(temp_cov)  # noqa
                changed = True

        if hasattr(obj, 'geo_coverage'):
            if len(obj.geo_coverage) > 0:
                geo_cov = obj.geo_coverage['geolocation']
                obj.geo_coverage['geolocation'] = fix_geographic_coverage(geo_cov)  # noqa
                changed = True

        if hasattr(obj, 'data_provenance'):
            if len(obj.data_provenance) > 0:
                data_prov = obj.data_provenance['data']
                new_provenance = {"dataProvenance": fix_data_provenance(data_prov)}  # noqa

                obj.data_provenance = new_provenance
                changed = True

        if changed:
            obj._p_changed = True
            obj.reindexObject()

        count += 1
        if count % 100 == 0:
            logger.info("Went through %s objects" % count)

    logger.info("Migrated temporal/geo/data provenance values")


def uninstall(context):
    """ Uninstall script
    """
    # Do something at the end of the uninstallation of this package.
