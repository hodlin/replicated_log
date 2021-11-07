import json, time
import grequests, requests
import threading
from concurrent.futures.thread import ThreadPoolExecutor
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
        self.stored_messages_id = set()
        self.messages_to_send = list()
        self.timeout = None
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def _send_message(self, message):
        header = {'content-type': 'application/json'}
        data = message.to_json()
        print(data)
        url = self.add_message_url
        print(f'Sending message to secondary #{self.id}')
        response = requests.post(url, data=data, headers=header, timeout=self.timeout)
        print(f'Response from secondary #{self.id} as follows: {response.json()}')
        if response is not None and response.status_code == 200:
            response_data = response.json()
            if response_data['result']:
                self.stored_messages_id.add(response_data['message_id'])
                self.messages_to_send[:] = [message for message in self.messages_to_send if not message.id == response_data['message_id']]

    def send_message(self, message):
        self.messages_to_send.append(message)
        print('Sending message in a thread..')
        # worker = threading.Thread(target=self._send_message, args=(message,))
        # worker.start()
        self.executor.submit(self._send_message, message)


    def __repr__(self):
        return f'SecondaryNode({self.host}:{self.port})'


class PrimaryNode:
    def __init__(self):
        self.messages = list()
        self.messages_ids = list()
        self.max_message_id = 0
        self.secondary_nodes = list()
        self.timeout = None
    
    def get_secondary_node(self, id, url):
        for secondary_node in self.secondary_nodes:
            if secondary_node.url == url:
                return secondary_node
        return SecondaryNode(id, *url.split(':'))

    def add_secondary_node(self, id, url):
        secondary_node_to_add = self.get_secondary_node(id, url)
        self.secondary_nodes.append(secondary_node_to_add)

    def add_message(self, message_body, write_consern):
        print('Adding message started')
        new_message_id = self.max_message_id + 1
        message = Message(new_message_id, message_body)
        print(f'Message id set to {new_message_id}')
        self.messages.append(message)
        self.messages_ids.append(new_message_id)
        self.max_message_id = max(self.messages_ids)
        print('Message added to the primary node')
        for secondary_node in self.secondary_nodes:
            secondary_node.send_message(message)
        # self.replicate_message(message)
        while True:
            message_copies = 0
            message_copies += 1 if new_message_id in self.messages_ids else 0
            for secondary in self.secondary_nodes:
                message_copies += 1 if new_message_id in secondary.stored_messages_id else 0
            if message_copies >= write_consern:
                return new_message_id
            time.sleep(1)
    
    # def message_saved_by_secondary(self,):

    # def replicate_message(self, message):
        
    #     header = {'content-type': 'application/json'}
    #     data = message.to_json()
    #     print(data)
    #     urls = [secondary_node.add_message_url for secondary_node in self.secondary_nodes]
    #     requests = [grequests.post(url, data=data, headers=header, timeout=self.timeout) for url in urls]
    #     responses = grequests.map(requests, size=len(self.secondary_nodes), exception_handler=exception_handler)
    #     for response, node in zip(responses, self.secondary_nodes):
    #         print(response)
    #         if response is not None and response.status_code == 200:
    #             response_data = response.json()
    #             if response_data['result']:
    #                 node.stored_messages_id.append(response_data['message_id'])

    def __repr__(self):
        return f'PrimaryNode({self.host}:{self.port})'