''' upgrade to 16 '''
import logging
from plone import api
from eea.coremetadata.utils import BlocksTraverser, \
    TemporalBlockTransformer, GeoBlockTransformer, \
    fix_temporal_coverage, fix_geographic_coverage


logger = logging.getLogger('eea.coremetadata.migration')


def run_upgrade(setup_context):
    """ run upgrade to 16
    """
    catalog = api.portal.get_tool("portal_catalog")
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

                obj.temporal_coverage['temporal'] = fix_temporal_coverage(temp_cov) # noqa
                changed = True

        if hasattr(obj, 'geo_coverage'):
            if len(obj.geo_coverage) > 0:
                geo_cov = obj.geo_coverage['geolocation']
                obj.geo_coverage['geolocation'] = fix_geographic_coverage(geo_cov) # noqa
                changed = True

        if changed:
            obj._p_changed = True
            obj.reindexObject()

        count += 1
        if count % 100 == 0:
            logger.info("Went through %s objects" % count)

    logger.info("Finished upgrade")
    return "Finished upgrade"
