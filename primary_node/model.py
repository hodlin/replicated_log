import json, time
import requests
from requests.exceptions import RequestException, HTTPError
import threading
import queue
from concurrent.futures.thread import ThreadPoolExecutor
from functools import total_ordering


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class CountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            self.lock.notifyAll()
        self.lock.release()

    def wait(self):
        self.lock.acquire()
        while self.count > 0:
            self.lock.wait()
        self.lock.release()


@total_ordering
class Message:
    def __init__(self, id, message, latch):
        self.id = id
        self.message = message
        self.latch = latch
        self._dict = {'id': self.id, 'message': self.message}

    def to_json(self):
        return json.dumps(self._dict, sort_keys=True, indent=4)
  
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
        self.get_health_url = self.url + '/get_health'
        self.get_stored_messages = self.url + '/get_stored_mesages'
        self.stored_messages = dict()
        self.stored_messages_id = set()
        self.send_executor = ThreadPoolExecutor(max_workers=3)
        self.messages_to_send = queue.PriorityQueue()
        self.timeout = 5
        self.is_healthy = False
        self.retry_timer = RepeatedTimer((self.timeout + 2) * 5 + 1, self.retry)
        self.get_health_timer = RepeatedTimer(self.timeout + 2, self.get_health)
    
    def _send_message(self, message):
        print(f'Sending message to node #{self.id}: {message} | {threading.get_ident()}')
        header = {'content-type': 'application/json'}
        data = message.to_json()
        url = self.add_message_url
        try:
            response = requests.post(url, data=data, headers=header, timeout=self.timeout)
            if response:
                print(f'Message is delivered to node #{self.id}: {message} | {threading.get_ident()}')
                response_data = response.json()
                self.stored_messages.update({response_data['message_id']: message})
                message.latch.count_down()
            else:
                raise HTTPError 
        except (RequestException) as e:
            # print(e)
            print(f'Message is not delivered to node #{self.id}: {message} | {threading.get_ident()}')
            with threading.Lock():
                self.messages_to_send.put(message)
            print(f'Message is put to retry queue at node #{self.id}: {message} | {threading.get_ident()}')

    def send_message(self, message):
        self.send_executor.submit(self._send_message, message)

    def retry(self):
        print(f'Retry procedure started for node #{self.id}.  | {threading.get_ident()}')
        if self.messages_to_send.empty():
            print(f'Node #{self.id} has no messages for retry. Skipping. | {threading.get_ident()}')
            return
        else:
            print(f'Node #{self.id} has messages for retry. | {threading.get_ident()}')
        if not self.is_healthy:
            print(f'Node #{self.id} is not available. Skipping. | {threading.get_ident()}')
            return
        messages_to_send = list()
        with threading.Lock():
            while not self.messages_to_send.empty():
                messages_to_send.append(self.messages_to_send.get())
        for message in messages_to_send:
            self.send_message(message)

    def get_health(self):
        with threading.Lock():
            previous_health_status = self.is_healthy
            is_healthy = None
            try:
                response = requests.get(self.get_health_url, timeout=self.timeout)
                # print(f'Heartbeat response from node #{self.id}: {response}')
                if response:
                    is_healthy = response.json()['is_healthy']
                    if not previous_health_status and is_healthy:
                        print(f'Remote state change detected. Cheking remote consistency on node {self.id} | {threading.get_ident()}')
                        self.check_remote_messages()
                else:
                    raise HTTPError
            except (RequestException) as e:
                # print(e)
                is_healthy = False
            print(f'Heartbeat to node #{self.id}: {is_healthy} | {threading.get_ident()}')
            self.is_healthy = is_healthy

    def check_remote_messages(self):
        try:
            response = requests.get(self.get_stored_messages, timeout=self.timeout)
            remote_message_ids = response.json()['message_ids']
            for id in self.stored_messages.keys():
                if id not in remote_message_ids:
                    message = self.stored_messages[id]
                    with threading.Lock():
                        self.messages_to_send.put(message)
                        print(f'Not delivered message found: {message}. Adding to retry queue on node #{self.id} | {threading.get_ident()}')
        except (RequestException) as e:
            print(f'Unable to get messages_list from remote node #{self.id} | {threading.get_ident()}')


    def __repr__(self):
        return f'SecondaryNode({self.id}, {self.host}:{self.port})'


class PrimaryNode:
    def __init__(self):
        self.id = 101
        self.messages = list()
        self.messages_ids = list()
        self.max_message_id = 0
        self.secondary_nodes = list()
        self.timeout = None
    
    def check_quorum(self):
        quorum_size = len(self.secondary_nodes) // 2 + 1
        available_nodes = 1
        for secondary in self.secondary_nodes:
            if secondary.is_healthy:
                available_nodes += 1
        return available_nodes >= quorum_size

    def get_secondary_node(self, id):
        for secondary_node in self.secondary_nodes:
            if secondary_node.id == id:
                return secondary_node
        return None

    def add_secondary_node(self, id, host, port):
        if self.get_secondary_node(id):
            return
        else:
            self.secondary_nodes.append(SecondaryNode(id, host, port))

    def send_message(self, message):
        self.messages.append(message)
        self.messages_ids.append(message.id)
        self.max_message_id = max(self.messages_ids)
        print(f'Message added to the primary node #{self.id}: {message} | {threading.get_ident()}')
        message.latch.count_down()

    def add_message(self, message_body, write_consern):
        if not self.check_quorum(): 
            return
        latch = CountDownLatch(write_consern)
        new_message_id = self.max_message_id + 1
        message = Message(new_message_id, message_body, latch)
        for node in [self, *self.secondary_nodes]:
            node.send_message(message)
        latch.wait()
        return new_message_id

        # while True:
        #     message_copies = 0
        #     message_copies += 1 if new_message_id in self.messages_ids else 0
        #     for secondary in self.secondary_nodes:
        #         message_copies += 1 if new_message_id in secondary.stored_messages_id else 0
        #     if message_copies >= write_consern:
        #         return new_message_id
        #     time.sleep(1)

    def messages_to_display(self):
        return [message for message in self.messages if message.latch.count <= 0]

    def __repr__(self):
        return f'PrimaryNode({self.host}:{self.port})'