

class SecondaryNode:
    def __init__(self, id, host, port):
        self.id = id
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}'
        self.add_message_url = self.url + '/add_message'
        self.stored_messages_id = list()

    def __repr__(self):
        return f'SecondaryNode({self.host}:{self.port})'