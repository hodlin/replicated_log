import sys
import json
from functools import total_ordering
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
    

messages = list()


app = Flask(__name__)

@app.route('/')
def index():
    return f'<p>Index page.</p>'

@app.route('/add_message', methods=['POST'])
def add_message():
    if request.method in ['POST']:
        response = dict()
        message_data = request.json
        print(message_data)
        if not message_data or message_data['id'] not in [message.id for message in messages]:
            messages.append(Message(**message_data))
            response = app.response_class(
                response=json.dumps({'id': message_data['id'], 'result': True}),
                status=200,
                mimetype='application/json'
            )
        else:
            response = app.response_class(
                response=json.dumps({'id': message_data['id'], 'result': False}),
                status=200,
                mimetype='application/json'
            )
    else:
        response = app.response_class(
                response=json.dumps(dict()),
                status=400,
                mimetype='application/json'
            )
    return response

@app.route('/list_messages', methods=['GET'])
def list_message():
    response = app.response_class(
        response=json.dumps([message.to_json() for message in sorted(messages)]),
        status=200,
        mimetype='application/json'
    )
    return response
    

if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith('-')]
    args = [args for args in sys.argv[1:] if not args.startswith('-')]
    named_args = dict(zip(opts, args))
    assert '-P' in named_args.keys()
    app.run(port=named_args['-P'], debug=True, threaded=True)
    