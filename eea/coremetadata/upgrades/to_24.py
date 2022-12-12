# pylint: disable=W1201, C0301, C0111, W0640, W1202
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
logger = logging.getLogger("eea.coremetadata.upgrade")


taxonomy_args = [
    {
        "name": "topics",
        "title": "EEA Coremetadata Topics taxonomy",
        "field_title": "Topics",
        "field_prefix": "",
        "description": "Topic selected from a predefined list for eea.coremetadata",  # noqa: E501
        "field_description": "Topics selected from a predefined list",
        "taxonomy_fieldset": "default",
        "default_language": "en"
    },
    {
        "name": "publisher",
        "title": "EEA Coremetadata Publisher taxonomy",
        "field_title": "Publisher",
        "field_prefix": "",
        "description": "Publishers selected from a predefined list for eea.coremetadata",  # noqa: E501
        "field_description": "Publishers selected from a predefined list",
        "taxonomy_fieldset": "ownership",
        "default_language": "en"
    },
    {
        "name": "other_organisations",
        "title": "EEA Coremetadata Organisations taxonomy",
        "field_title": "Organisations",
        "field_prefix": "",
        "description": "Organisations selected from a predefined list for eea.coremetadata",  # noqa: E501
        "field_description": "Organisations selected from a predefined list",
        "taxonomy_fieldset": "ownership",
        "default_language": "en"
    }
]


def to_24(context):
    """ Add behaviors for core metadata taxonomies """
    sm = context.aq_parent.getSiteManager()

    for new_args in taxonomy_args:
        behavior = TaxonomyBehavior(**new_args)

        sm.registerUtility(behavior, IBehavior, name=new_args["name"])

    taxonomy_args[0]["vocabulary_name"] = 'collective.taxonomy.eeatopicstaxonomy'  # noqa: E501
    taxonomy_args[0]["short_name"] = "topics"
    taxonomy_args[0]["field_name"] = (taxonomy_args[0]['field_prefix'] or "") + taxonomy_args[0]['short_name']  # noqa: E501

    taxonomy_args[1]["vocabulary_name"] = 'collective.taxonomy.eeapublishertaxonomy'  # noqa: E501
    taxonomy_args[1]["short_name"] = "publisher"
    taxonomy_args[1]["field_name"] = (taxonomy_args[1]['field_prefix'] or "") + taxonomy_args[1]['short_name']  # noqa: E501

    taxonomy_args[2]["vocabulary_name"] = 'collective.taxonomy.eeaorganisationstaxonomy'  # noqa: E501
    taxonomy_args[2]["short_name"] = "other_organisations"
    taxonomy_args[2]["field_name"] = (taxonomy_args[2]['field_prefix'] or "") + taxonomy_args[2]['short_name']  # noqa: E501

    for new_args in taxonomy_args:
        sm.registerAdapter(
            TaxonomyIndexer(new_args['field_name'], new_args['vocabulary_name']),  # noqa: E501
            (IDexterityContent, IZCatalog),
            IIndexer,
            name=new_args['field_name'],
        )

        catalog = getToolByName(context.aq_parent, "portal_catalog")

        try:
            catalog.delIndex(new_args['field_name'])
            catalog.delColumn(new_args['field_name'])
        except CatalogError:
            logging.info(
                "Index {0} doesn't exists".format(new_args['field_name'])  # noqa: E501
            )

        idx_object = KeywordIndex(str(new_args['field_name']))
        try:
            catalog.addIndex(new_args['field_name'], idx_object)
        except CatalogError:
            logging.info(
                "Index {0} already exists, we hope it is proper configured".format(  # noqa: E501
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

        add("title", Record(field.TextLine(), safe_unicode(new_args['field_title'])))  # noqa: E501
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
            "vocabulary", Record(field.TextLine(), safe_unicode(new_args['vocabulary_name']))  # noqa: E501
        )  # noqa: E501
        add("fetch_vocabulary", Record(field.Bool(), True))
        add("sortable", Record(field.Bool(), False))
        add("description", Record(field.Text(), safe_unicode("")))
