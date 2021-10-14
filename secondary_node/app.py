from gevent import monkey
monkey.patch_all()
import json
from flask import Flask
from flask import request, make_response
from model import SecondaryNode

secondary_node = SecondaryNode()

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
        message_added = secondary_node.add_message(**message_data)
        if message_added:
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
        response=json.dumps([message.to_json() for message in secondary_node.messages_to_display()]),
        status=200,
        mimetype='application/json'
    )
    return response
    

if __name__ == '__main__':
    # opts = [opt for opt in sys.argv[1:] if opt.startswith('-')]
    # args = [args for args in sys.argv[1:] if not args.startswith('-')]
    # named_args = dict(zip(opts, args))
    # assert '-P' in named_args.keys()
    # app.run(port=named_args['-P'], debug=True, threaded=True)
    app.run(host='0.0.0.0', threaded=True)
    