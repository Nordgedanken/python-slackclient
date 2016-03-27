#!/usr/bin/python
# mostly a proxy object to abstract how some of this works

import json

from slackclient._server import Server


class SlackClient(object):
    def __init__(self, token):
        self.token = token
        self.server = Server(self.token, False)

    def rtm_connect(self):
        try:
            self.server.rtm_connect()
            return True
        except:
            return False

    def api_call(self, method, **kwargs):
        result = json.loads(self.server.api_call(method, **kwargs))
        if self.server and result.get("ok", None):
            if method == 'im.open':
                self.server.attach_channel(kwargs["user"], result["channel"]["id"])
            elif method in ('mpim.open', 'groups.create', 'groups.createchild'):
                self.server.attach_channel(result['group']['name'], result['group']['id'], result['group']['members'])
            elif method in ('channels.create', 'channels.join'):
                self.server.attach_channel(result['channel']['name'], result['channel']['id'], result['channel']['members'])
        return result

    def rtm_read(self):
        # in the future, this should handle some events internally i.e. channel
        # creation
        if self.server:
            json_data = self.server.websocket_safe_read()
            data = [json.loads(d) for d in json_data.splitlines()]
            for item in data:
                self.process_changes(item)
            return data
        else:
            raise SlackNotConnected

    def rtm_send_message(self, channel, message):
        return self.server.channels.find(channel).send_message(message)

    def process_changes(self, data):
        if "type" in data.keys():
            if data["type"] in ('channel_created', 'group_joined'):
                channel = data["channel"]
                self.server.attach_channel(channel["name"], channel["id"], [])
            if data["type"] == 'im_created':
                channel = data["channel"]
                self.server.attach_channel(channel["user"], channel["id"], [])
            if data["type"] == "team_join":
                user = data["user"]
                self.server.parse_user_data([user])
            pass


class SlackNotConnected(Exception):
    pass
