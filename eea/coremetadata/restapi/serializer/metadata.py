""" Adapter for creators_fullname and contributors_fullname
"""

import copy
from eea.coremetadata.metadata import ICoreMetadata
from zope.schema.interfaces import ITuple
from zope.interface import Interface
from zope.component import adapter
from zope.interface import implementer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.interfaces import IFieldSerializer
from plone.dexterity.interfaces import IDexterityContent
from plone import api


@implementer(IFieldSerializer)
@adapter(ITuple, IDexterityContent, Interface)
class CreatorsFieldSerializer(DefaultFieldSerializer):
    """Creators and Contributors field serializer"""

    def __call__(self):
        value = copy.deepcopy(self.get_value())
        if self.field is ICoreMetadata["creators_fullname"]:
            user_ids = getattr(self.context, "creators", [])
        elif self.field is ICoreMetadata["contributors_fullname"]:
            user_ids = getattr(self.context, "contributors", [])
        else:
            return json_compatible(value)

        fullnames = []
        for userid in user_ids:
            user = api.user.get(userid)
            if user:
                fullname = user.getProperty("fullname", "")
                fullnames.append(fullname if fullname else userid)
            else:
                fullnames.append(userid)

        return json_compatible(fullnames)
