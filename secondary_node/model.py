import json
from functools import total_ordering


@total_ordering
class Message:
    def __init__(self, id, message):
        self.id = id
        self.message = message

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
  
    def __ge__(self, obj):
        return ((self.id) >= (obj.id))

    def __repr__(self):
        return f'Message({self.id}, {self.message[:10]})'


class SecondaryNode:
    def __init__(self):
        self.messages = list()
        self.messages_ids = list()
        self.delay = 0

    def add_message(self, id, message):
        if id not in self.messages_ids:
            self.messages.append(Message(id, message))
            self.messages_ids.append(id)
            return True
        else: 
            return False

    def messages_to_display(self):
        return self.messages

    def set_delay(self, delay):
        self.delay = delay

    def __repr__(self):
        return f'SecondaryNode({self.id}, {self.host}:{self.port})'