import sys
import json
from flask import Flask
from flask import request, make_response
from models import PrimaryNode

primary_node = PrimaryNode()

app = Flask(__name__)

@app.route('/')
def index():
    return f'<p>Index page.</p>'

@app.route('/add_secondary', methods=['POST'])
def add_secondary_node():
    primary_node.add_secondary_node(f'{request.json["host"]}:{request.json["port"]}')
    response = make_response(f'OK!', 200)
    return response

@app.route('/add_message', methods=['POST'])
def add_message():
    if request.method == 'POST':
        message_data = request.json
        id = primary_node.add_message(message_data['message'])
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
    if '-P' in named_args.keys():
        app.run(port=named_args['-P'], debug=True, threaded=True)
    else:
        app.run(port=5000, debug=True, threaded=True)