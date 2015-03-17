"""Gateway for accessing the Discourse API (for forums)"""

import json
import re
from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class Error(Exception):
    pass


class UserClient(object):
    """An API client for interacting with Discourse"""

    def __init__(self, api_client):
        self._api_client = api_client

    # USER ACTIONS

    @ndb.tasklet
    def getUserByEmail(self, user_email):
        """Finds a user with the given email

        This method takes a user email and returns a future which resolves to
        the Discourse user with that email address, if they exist. If no user
        is found, None is returned.
        """
        users = yield self._api_client.getRequest(
            'admin/users/list/active.json',
            params={'filter': user_email, 'show_emails': 'true'}
        )

        for user in users:
            if user['email'].lower() == user_email.lower():
                raise ndb.Return(user)

        raise ndb.Return(None)

    @ndb.tasklet
    def createUser(self, name, email, password, username, external_id=None):
        """Create a Discourse account

        This method takes a user object and returns the Discourse API response
        containing the user information for that user.
        """

        payload = {
            'username': username,
            'email': email,
            'name': name,
            'password': password,
            'active': 'true',
        }

        if external_id:
            payload['external_id'] = external_id

        response = yield self._api_client.postRequest('users/', payload=payload)
        raise ndb.Return(response)

    @ndb.tasklet
    def deleteUser(self, email):
        user = yield self.getUserByEmail(email)
        if user is None:
            raise ndb.Return(None)

        response = yield self._api_client.deleteRequest('admin/users/%s.json' % user['id'])
        raise ndb.Return(response)

    # CONTENT ACTIONS

    @ndb.tasklet
    def createPost(self, text, title, category_name, **kwargs):
        """Creates a post"""

        category = yield self.getCategoryByName(category_name)

        payload = {
            'raw': text,
            'title': title,
            'category': category['id']
        }

        for k, v in kwargs.iteritems():
            payload[k] = v

        response = yield self._api_client.postRequest('posts', payload=payload)
