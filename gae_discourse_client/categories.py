"""Gateway for accessing the Discourse API (for forums)"""

import json
import re
from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class Error(Exception):
    pass


class CategoryClient(object):
    """An API client for interacting with Discourse"""

    def __init__(self, api_client):
        self._api_client = api_client

    @ndb.tasklet
    def getCategoryByName(self, category_name):
        categories = yield self._api_client.getRequest('categories.json')

        for category in categories['category_list']['categories']:
            if category['name'] == category_name:
                raise ndb.Return(category)

        raise ndb.Return(None)

    @ndb.tasklet
    def createCategory(self, category_name, parent_category_name=None, **kwargs):
        """Create a category"""
        category = yield self.getCategoryByName(category_name)
        if category:
            raise ndb.Return(None)

        defaults = {
            'color': 'FFFFFF',
            'text_color': '000000'
        }

        payload = {
            'name': category_name,
            'allow_badges': True
        }

        payload.update(defaults)

        for k, v in kwargs.iteritems():
            payload[k] = v

        if parent_category_name:
            parent_category = yield self.getByName(parent_category_name)
            if not parent_category:
                raise Error("Could not find category named %s" % parent_category_name)
            payload['parent_category_id'] = parent_category['id']

        response = yield self._api_client.postRequest('categories', payload=payload)
        raise ndb.Return(response)

    @ndb.tasklet
    def deleteCategory(self, category_name):
        category = yield self.getCategoryByName(category_name)
        if not category:
            raise ndb.Return(None)

        response = yield self._api_client.deleteRequest('categories/%s' % category['slug'])
        raise ndb.Return(response)
