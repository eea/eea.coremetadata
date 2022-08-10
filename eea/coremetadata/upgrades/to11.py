''' upgrade to 11 '''
# import transaction

from collections import deque
import json
import logging
from plone import api


logger = logging.getLogger('eea.coremetadata.migration')


def iterate_children(value):
    """iterate_children.
    :param value:
    """
    queue = deque(value)

    while queue:
        child = queue.pop()
        yield child
        if child.get("children"):
            queue.extend(child["children"] or [])


def fix_geographic_coverage(geo_cov):
    new_geo_cov = []
    for coverage in geo_cov:
        # add other fields present in geo_cov
        updated_coverage = {
            "title": coverage['label'],
            "geonamesID": int(coverage['value'].split('-')[-1])
        }
        new_geo_cov.append(updated_coverage)

    import pdb; pdb.set_trace()
    return new_geo_cov


def fix_temporal_coverage(temp_cov):
    temp_values = [temp['value'] for temp in temp_cov]
    new_values = []

    for val in temp_values:
        if '-' in val:
            start, end = val.split('-')
            new_values.extend(list(range(int(start), int(end) + 1)))
        else:
            new_values.append(int(val))

    # remove duplicates and sort list
    new_values = list(set(new_values))
    new_values.sort()

    return new_values


class TemporalBlockTransformer(object):
    """TemporalBlockTransformer."""

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        if 'temporal' in block:
            block['temporal'] = fix_temporal_coverage(block['temporal'])
            return True

        if (block or {}).get('@type') == 'temporal':
            if 'value' not in block:        # avoid empty blocks
                return None

            block['value'] = fix_temporal_coverage(block['value'])
            return True

        return None


class GeoBlockTransformer(object):
    """GeoBlockTransformer."""

    def __init__(self, context):
        self.context = context

    def __call__(self, block):
        if 'geolocation' in block:
            block['geolocation'] = fix_geographic_coverage(block['geolocation'])
            return True

        if (block or {}).get('@type') == 'geolocation':
            if 'value' not in block:        # avoid empty blocks
                return None

            block['value'] = fix_geographic_coverage(block['value'])
            return True

        return None


def get_blocks(obj):
    """ get_blocks """
    blocks_layout = getattr(obj, 'blocks_layout', {})

    if isinstance(blocks_layout, str):
        blocks_layout = json.loads(blocks_layout)
        obj.blocks_layout = blocks_layout
        obj._p_changed = True
        logger.info('Converted str blocks_layout for % s',
                    obj.absolute_url())

    order = blocks_layout.get('items', [])

    blocks = getattr(obj, 'blocks', {})
    if isinstance(blocks, str):
        blocks = json.loads(blocks)
        obj.blocks = blocks
        obj._p_changed = True
        logger.info('Converted str blocks for % s',
                    obj.absolute_url())

    out = []
    for _id in order:
        if _id not in blocks:
            obj.blocks_layout['items'] = [b for b in order if b in blocks]
            obj._p_changed = True
            logger.info("Object with incomplete blocks %s", obj.absolute_url())
            continue
        out.append((_id, blocks[_id]))

    return out


class BlocksTraverser(object):
    """ BlocksTraverser """

    def __init__(self, context):
        self.context = context

    def __call__(self, visitor):

        for (_, block_value) in get_blocks(self.context):

            if visitor(block_value):
                self.context._p_changed = True

            self.handle_subblocks(block_value, visitor)

    def handle_subblocks(self, block_value, visitor):
        """ handle_subblocks """

        if "data" in block_value and isinstance(block_value["data"], dict) \
                and "blocks" in block_value["data"]:
            for block in block_value["data"]["blocks"].values():
                if visitor(block):
                    self.context._p_changed = True

                self.handle_subblocks(block, visitor)

        if "blocks" in block_value:
            for block in block_value['blocks'].values():
                if visitor(block):
                    self.context._p_changed = True

                self.handle_subblocks(block, visitor)


def run_upgrade(setup_context):
    """ run upgrade to 1003
    """
    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog(_nonsense=True)

    water_geo = {"geolocation":[{"label": "Cyprus", "value": "geo-146669"},{"label": "Portugal", "value": "geo-2264397"},]}
    water_temporal = {"temporal":[{"__isNew__": True, "label": "2010-2019", "value": "2010-2019"}, {"value": "2006", "label": "2006"}, {"value": "2011", "label": "2011"}]}

    eea_geo = {"geolocation": [{"value": "geo-732800", "label": "Bulgaria"}, {"value": "geo-3202326", "label": "Croatia"}], "readOnly": True}
    eea_temporal = {"readOnly": True, "temporal": [{"value": "2005", "label": "2005"}, {"value": "2006", "label": "2006"}]}

    blocks_temporal = {"temporal": [{"value": "2016", "label": "2016"}, {"value": "2017", "label": "2017"}]}
    blocks_geo = {"geolocation": [{"group": ["EEA32", "EEA33", "EEA39", "EU15", "EU25", "EU27", "EU28", "Pan-Europe"], "value": "geo-2782113", "label": "Austria"},
                                  {"group": ["EEA32", "EEA33", "EEA39", "EU15", "EU25", "EU27", "EU28", "Pan-Europe"], "value": "geo-2802361", "label": "Belgium"},
                                  {"group": ["EEA32", "EEA33", "EEA39", "EU27", "EU28", "Pan-Europe"], "value": "geo-732800", "label": "Bulgaria"}]}

    correct_temporal = {"temporal": [2000,2001,2002]}
    correct_geo = {"geoCoverage": [{"title": "Bulgaria", "geonamesID": 732800}]}

    for brain in brains:
        obj = brain.getObject()
        changed = False

        # if hasattr(obj.aq_inner.aq_self, 'blocks') and \
        #         hasattr(obj.aq_inner.aq_self, 'blocks_layout'):
        #
        #     traverser = BlocksTraverser(obj)
        #
        #     temporal_fixer = TemporalBlockTransformer(obj)
        #     geolocation_fixer = GeoBlockTransformer(obj)
        #
        #     traverser(temporal_fixer)
        #     traverser(geolocation_fixer)

        if hasattr(obj, 'temporal_coverage'):
            changed = True
            temp_cov = obj.temporal_coverage['temporal']

            obj.temporal_coverage['temporal'] = fix_temporal_coverage(temp_cov)

        if hasattr(obj, 'geo_coverage'):
            changed = True
            geo_cov = obj.geo_coverage['geolocation']

            vals = fix_geographic_coverage(geo_cov)
            vals = fix_geographic_coverage(water_geo)
            vals = fix_geographic_coverage(eea_geo)

            obj.geo_coverage = {"geoCoverage": fix_geographic_coverage(geo_cov)}

        if changed:
            obj._p_changed = True
            obj.reindexObject()


    logger.info("Finished upgrade")
    import pdb;pdb.set_trace()
    return 'xxx'
