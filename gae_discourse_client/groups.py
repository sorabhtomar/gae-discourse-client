"""Gateway for accessing the Discourse API (for forums)"""

import json
import re
from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class Error(Exception):
    pass


class GroupClient(object):
    """An API client for interacting with Discourse"""

    def __init__(self, api_client):
        self._api_client = api_client

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
    def addUserToGroup(self, user_email, group_name):
        """Adds the given account to the Discourse group with the given name"""

        user = yield self.getUserByEmail(user_email)
        if not user:
            raise Error("Unable to find user with email %s" % user_email)

        groups = yield self._api_client.getRequest('admin/groups.json')

        group_id = None
        for group in groups:
            if group['name'] == group_name:
                group_id = group['id']
                break
        else:
            raise Error("Group named %s not found" % group_name)

        payload = {
            'usernames': user['username']
        }

        result = yield self._api_client.putRequest(
            'admin/groups/%s/members.json' % group_id, payload=payload
        )
        raise ndb.Return(result)

    @ndb.tasklet
    def removeUserFromGroup(self, user_email, group_name):
        """Removes an account from a group"""

        user = yield self.getUserByEmail(user_email)
        if not user:
            raise Error("Unable to find user with email %s" % user_email)

        group = yield self.getGroupByName(group_name)
        if not group:
            raise Error("Group named %s not found" % group_name)

        result = yield self._api_client.deleteRequest(
            'admin/groups/%s/members.json' % group['id'],
            params={'user_id': user['id']}
        )
        raise ndb.Return(result)

    @ndb.tasklet
    def createGroup(self, group_name, **kwargs):
        """Creates a group with the given name on Discourse"""

        groups = yield self._api_client.getRequest('admin/groups.json')

        for group in groups:
            if group['name'] == group_name:
                raise ndb.Return(None)
                # raise Error("Group named %s already exists!" % group_name)

        payload = {
            'name': group_name
        }

        for k, v in kwargs.iteritems():
            payload[k] = v

        response = yield self._api_client.postRequest('admin/groups', payload=payload)
        raise ndb.Return(response)

    @ndb.tasklet
    def deleteGroup(self, group_name):
        group = yield self.getGroupByName(group_name)
        if not group:
            raise ndb.Return(None)

        response = yield self._api_client.deleteRequest('admin/groups/%s' % group['id'])
        raise ndb.Return(response)

    @ndb.tasklet
    def getGroupByName(self, group_name):
        groups = yield self._api_client.getRequest('admin/groups.json')

        for group in groups:
            if group['name'] == group_name:
                raise ndb.Return(group)

        raise ndb.Return(None)
