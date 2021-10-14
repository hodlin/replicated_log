import json
import grequests
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
    def __init__(self, id, host, port):
        self.id = id
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}'
        self.add_message_url = self.url + '/add_message'
        self.stored_messages_id = list()

    def __repr__(self):
        return f'SecondaryNode({self.host}:{self.port})'


class PrimaryNode:
    def __init__(self):
        self.messages = list()
        self.messages_ids = list()
        self.max_message_id = 0
        self.secondary_nodes = list()
    
    def get_secondary_node(self, url):
        max_id = 0
        for secondary_node in self.secondary_nodes:
            max_id = secondary_node.id if secondary_node.id > max_id else max_id
            if secondary_node.url == url:
                return secondary_node
        return SecondaryNode(max_id + 1, *url.split(':'))

    def add_secondary_node(self, url):
        secondary_node_to_add = self.get_secondary_node(url)
        self.secondary_nodes.append(secondary_node_to_add)

    def add_message(self, message_body):
        new_message_id = self.max_message_id + 1
        message = Message(new_message_id, message_body)
        self.messages.append(message)
        self.messages_ids.append(new_message_id)
        self.max_message_id = max([id for id in self.messages_ids])
        self.replicate_message(message)
        return new_message_id
        
    def replicate_message(self, message):
        def exception_handler(request, exception):
            print(f'Request failed: {request}')
            print(f'exception {exception}')
            return None
        header = {'content-type': 'application/json'}
        data = message.to_json()
        urls = [secondary_node.add_message_url for secondary_node in self.secondary_nodes]
        requests = [grequests.post(url, data=data, headers=header, timeout=1) for url in urls]
        responses = grequests.map(requests, size=len(self.secondary_nodes), exception_handler=exception_handler)
        for response, node in zip(responses, self.secondary_nodes):
            print(response)
            if response is not None and response.status_code == 200:
                response_data = response.json()
                if response_data['result']:
                    node.stored_messages_id.append(response_data['id'])

    def __repr__(self):
        return f'PrimaryNode({self.host}:{self.port})'