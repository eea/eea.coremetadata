""" GET
"""
# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.pas.plugin import JWTAuthenticationPlugin
from plone.restapi.services import Service
from zope.publisher.interfaces import IPublishTraverse
from zope.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.interface import alsoProvides
from Products.CMFCore.utils import getToolByName
from urllib.parse import parse_qs
from uuid import uuid4
from plone import api

import plone.protect.interfaces

PREVIEW_TOKEN = "PreviewToken"


class PreviewLinkGet(Service):
    """Get Preview link information"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.params = []
        portal = getSite()
        self.portal_membership = getToolByName(portal, "portal_membership")

    def get_preview_link(self, token):
        url = self.request["ACTUAL_URL"]
        preview_url = f"{url}?preview=true&id={token}"
        return preview_url.replace("/@preview-link", "")

    def reply(self):
        """Reply"""
        result = {}
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        enabled = self.request.form.get("enabled", False)
        if enabled == "true":
            plugin_preview = JWTAuthenticationPlugin(
                "preview_jwt", "JWT preview plugin"
            )
            token = plugin_preview.create_token(userid="admin")
            # token = uuid4().hex
            annotations = IAnnotations(self.context)
            annotations[PREVIEW_TOKEN] = token
            preview_link = self.get_preview_link(token)
            result = {"enabled": enabled, "link": preview_link, "token": token}
            return result

        result = {"enabled": enabled}
        return result
