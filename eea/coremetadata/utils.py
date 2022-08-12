''' utils '''
from collections import deque
import json


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
        if 'geonamesID' and 'title' in coverage:
            new_geo_cov.append(coverage)
            continue

        updated_coverage = {
            "title": coverage['label'],
            "geonamesID": int(coverage['value'].split('-')[-1])
        }

        # add other fields present in geo_cov
        for key in coverage.keys():
            if key not in updated_coverage and key not in ['label', 'value']:
                updated_coverage.update({key: coverage[key]})

        new_geo_cov.append(updated_coverage)

    return new_geo_cov


def fix_temporal_coverage(temp_cov):
    if all([isinstance(temp, int) for temp in temp_cov]):
        return temp_cov

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
            block['geolocation'] = fix_geographic_coverage(block['geolocation']) # noqa
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
