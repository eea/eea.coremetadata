""" GET
"""
# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zope.publisher.interfaces import IPublishTraverse
from zope.component.hooks import getSite
from zope.interface import implementer
from Products.CMFCore.utils import getToolByName
from urllib.parse import parse_qs
from uuid import uuid4
from plone import api


@implementer(IPublishTraverse)
class PreviewLinkGet(Service):
    """Get Preview link information"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.params = []
        portal = getSite()
        self.portal_membership = getToolByName(portal, "portal_membership")

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    def get_preview_link(self):
        url = self.request["ACTUAL_URL"]
        preview_url = f"{url}/?id={uuid4()}&preview=true"
        return preview_url.replace("/@preview-link", "")

    def reply(self):
        """Reply"""
        result = {}
        enabled = self.request.form.get("enabled", False)
        if enabled == "true":
            preview_link = self.get_preview_link()
            result = {"enabled": enabled, "link": preview_link}
            return result

        result = {"enabled": enabled}
        return result
