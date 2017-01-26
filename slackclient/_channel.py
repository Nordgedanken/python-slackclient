class Channel(object):
    '''
    A Channel represents a public or private Slack Channel instance
    '''
    def __init__(self, server, name, channel_id, members=None):
        self.server = server
        self.name = name
        self.id = channel_id
        self.members = members or []

    def __eq__(self, compare_str):
        if (compare_str in (self.id, self.name) or
           "#" + compare_str == self.name):
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "\n".join("{0} : {1:.40}".format(key, value) for key, value
                         in self.__dict__.items())

    def __repr__(self):
        return self.__str__()

    def send_message(self, message, thread=None, reply_broadcast=False):
        '''
        Sends a message to a this Channel.

        Include the parent message's thread_ts value in `thread`
        to send to a thread.

        :Args:
            message (message) - the string you'd like to send to the channel
            thread (str or None) - the parent message ID, if sending to a
                thread
            reply_broadcast (bool) - if messaging a thread, whether to
                also send the message back to the channel

        :Returns:
            None
        '''
        message_json = {"type": "message", "channel": self.id, "text": message}
        if thread is not None:
            message_json["thread_ts"] = thread
            if reply_broadcast:
                message_json['reply_broadcast'] = True

        self.server.send_to_websocket(message_json)
