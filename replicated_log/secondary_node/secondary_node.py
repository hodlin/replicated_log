from message import Message

class SecondaryNode:
    def __init__(self):
        self.messages = list()
        self.messages_ids = list()

    def add_message(self, id, message):
        if id not in self.messages_ids:
            self.messages.append(Message(id, message))
            self.messages_ids.append(id)
            return True
        else: 
            return False

    def messages_to_display(self):
        return self.messages

    def __repr__(self):
        return f'SecondaryNode({self.id}, {self.host}:{self.port})'