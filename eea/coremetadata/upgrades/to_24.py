# pylint: disable=W1201
# -*- coding: utf-8 -*-
""" Upgrade to 2.4 """
import logging
from zope.component import getUtility
from collective.taxonomy.behavior import TaxonomyBehavior
from collective.taxonomy.indexer import TaxonomyIndexer
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.interfaces import IIndexer
from plone.registry import Record, field
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
from Products.ZCatalog.Catalog import CatalogError
from Products.ZCatalog.interfaces import IZCatalog
from eea.coremetadata import EEAMessageFactory as _
logger = logging.getLogger("eea.coremetadata.upgrade")


def to_24(context):
    """ Add behaviors for core metadata taxonomies """
    new_args = {}
    new_args["name"] = "topics"
    new_args["title"] = "EEA Coremetadata Topics taxonomy"
    new_args["field_title"] = "Topics"
    new_args["field_prefix"] = ""
    new_args["description"] = "Topic selected from a predefined list for eea.coremetadata"
    new_args["field_description"] = new_args["description"]
    new_args["taxonomy_fieldset"] = "default"
    new_args["default_language"] = "en"

    sm = context.aq_parent.getSiteManager()

    behavior = TaxonomyBehavior(**new_args)

    sm.registerUtility(behavior, IBehavior, name=new_args["name"])

    new_args["vocabulary_name"] = 'collective.taxonomy.eeatopicstaxonomy'
    new_args["short_name"] = "topics"
    new_args["field_name"] = (new_args['field_prefix'] or "") + new_args['short_name']


    sm.registerAdapter(
        TaxonomyIndexer(new_args['field_name'], new_args['vocabulary_name']),
        (IDexterityContent, IZCatalog),
        IIndexer,
        name=new_args['field_name'],
    )

    catalog = getToolByName(context.aq_parent, "portal_catalog")

    try:
        catalog.delIndex("topics")
        catalog.delColumn("topics")
    except CatalogError:
        logging.info(
            "Index {0} doesn't exists".format(new_args['field_name'])  # noqa: E501
        )

    idx_object = KeywordIndex(str(new_args['field_name']))
    try:
        catalog.addIndex(new_args['field_name'], idx_object)
    except CatalogError:
        logging.info(
            "Index {0} already exists, we hope it is proper configured".format(
                new_args['field_name']
            )  # noqa: E501
        )

    try:
        catalog.addColumn(new_args['field_name'])
    except CatalogError:
        logging.info(
            "Column {0} already exists".format(new_args['field_name'])
        )  # noqa: E501

    registry = getUtility(IRegistry)
    prefix = "plone.app.querystring.field." + new_args['field_name']

    def add(name, value):
        registry.records[prefix + "." + name] = value

    add("title", Record(field.TextLine(), safe_unicode(new_args['field_title'])))
    add("enabled", Record(field.Bool(), True))
    add("group", Record(field.TextLine(), safe_unicode("Taxonomy")))
    add(
        "operations",
        Record(
            field.List(value_type=field.TextLine()),
            ["plone.app.querystring.operation.selection.is"],
        ),
    )
    add(
        "vocabulary", Record(field.TextLine(), safe_unicode(new_args['vocabulary_name']))
    )  # noqa: E501
    add("fetch_vocabulary", Record(field.Bool(), True))
    add("sortable", Record(field.Bool(), False))
    add("description", Record(field.Text(), safe_unicode("")))


# (Pdb) pp vars(self)
# {'default_language': 'en',
#  'description': '',
#  'factory': None,
#  'field_description': '',
#  'field_prefix': 'taxonomy_',
#  'field_title': 'Organisations',
#  'is_required': False,
#  'is_single_select': False,
#  'name': 'collective.taxonomy.generated.eeaorganisationstaxonomy',
#  'taxonomy_fieldset': 'ownership',
#  'title': 'Organisations',
#  'write_permission': ''}
# (Pdb) self.vocabulary_name
# 'collective.taxonomy.eeaorganisationstaxonomy'
# (Pdb) self.field_name
# 'taxonomy_eeaorganisationstaxonomy'



# (Pdb) pp vars(self)
# {'default_language': 'en',
#  'description': '',
#  'factory': None,
#  'field_description': '',
#  'field_prefix': 'taxonomy_',
#  'field_title': 'Publisher',
#  'is_required': False,
#  'is_single_select': False,
#  'name': 'collective.taxonomy.generated.eeapublishertaxonomy',
#  'taxonomy_fieldset': 'ownership',
#  'title': 'Publisher',
#  'write_permission': ''}
# (Pdb) self.vocabulary_name
# 'collective.taxonomy.eeapublishertaxonomy'
# (Pdb) self.field_name
# 'taxonomy_eeapublishertaxonomy'


# (Pdb) pp vars(self)
# {'default_language': 'en',
#  'description': 'Topic selected from a predefined list',
#  'factory': None,
#  'field_description': 'Topic selected from a predefined list',
#  'field_prefix': 'taxonomy_',
#  'field_title': 'Topics',
#  'is_required': False,
#  'is_single_select': False,
#  'name': 'collective.taxonomy.generated.eeatopicstaxonomy',
#  'taxonomy_fieldset': 'default',
#  'title': 'Topics',
#  'write_permission': ''}
# (Pdb) self.vocabulary_name
# 'collective.taxonomy.eeatopicstaxonomy'
# (Pdb) self.field_name
# 'taxonomy_eeatopicstaxonomy'
