import re
import sys
import json
from functools import total_ordering
import grequests
from flask import Flask
from flask import request, make_response
from werkzeug.wrappers import response

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
    
    def add_secondary_node(self, id, url):
        secondary_node = SecondaryNode(id, *url.split(':'))
        self.secondary_nodes.append(secondary_node)

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

primary_node = PrimaryNode()

app = Flask(__name__)

@app.route('/')
def index():
    return f'<p>Index page.</p>'

@app.route('/add_message', methods=['GET', 'POST'])
def add_message():
    if request.method in ['GET', 'POST']:
        message_body = request.args.get('message')
        id = primary_node.add_message(message_body)
        response = make_response(f'Message saved with id {id}', 200)
    else:
        response = make_response("Bad request", 400)
    return response

@app.route('/list_messages', methods=['GET'])
def list_message():
    response = app.response_class(
        response=json.dumps([message.to_json() for message in primary_node.messages]),
        status=200,
        mimetype='application/json'
    )
    return response
    

if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith('-')]
    args = [args for args in sys.argv[1:] if not args.startswith('-')]
    named_args = dict(zip(opts, args))
    assert '-P' in named_args.keys()
    # assert '-h1' in named_args.keys()
    assert '-p1' in named_args.keys()
    # assert '-h2' in named_args.keys()
    assert '-p2' in named_args.keys()
    primary_node.add_secondary_node(1, f'localhost:{named_args["-p1"]}')
    primary_node.add_secondary_node(2, f'localhost:{named_args["-p2"]}')
    print(primary_node.secondary_nodes)
    # primary_node.add_secondary_node(2, f'localhost:{named_args["-p2"]}')
    app.run(port=named_args['-P'], debug=True, threaded=True)