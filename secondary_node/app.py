import sys
import json
import time
from flask import Flask
from flask import request, make_response
from model import SecondaryNode

secondary_node = None

app = Flask(__name__)

@app.route('/')
def index():
    return f'<p>Index page.</p>'

@app.route('/add_message', methods=['POST'])
def add_message():
    time.sleep(secondary_node.delay)
    if request.method in ['POST']:
        message_data = request.json
        print(message_data)
        message_added = secondary_node.add_message(message_data['id'], message_data['message'])
        if message_added:
            response = app.response_class(
                response=json.dumps({'node_id': secondary_node.id, 'message_id': message_data['id'], 'result': True}),
                status=200,
                mimetype='application/json'
                )
        else:
            response = app.response_class(
                status=500,
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
        response=json.dumps({'messages': [message.to_json() for message in secondary_node.messages_to_display()]}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/get_id', methods=['GET'])
def get_id():
    response = app.response_class(
                response=json.dumps({'id': secondary_node.id}),
                status=200,
                mimetype='application/json'
                )   
    return response

@app.route('/set_delay', methods=['post'])
def set_delay():
    if request.method in ['POST']:
        delay_data = request.json
        secondary_node.set_delay(delay_data['delay'])
    return make_response(f'Delay set to {secondary_node.delay}', 200)

@app.route('/get_health', methods=['get'])
def get_health():
    time.sleep(secondary_node.delay)
    if request.method in ['GET']:
        response = app.response_class(
                response=json.dumps({'node_id': secondary_node.id, 'is_healthy': True}),
                status=200,
                mimetype='application/json'
                )
    else:
        response = app.response_class(
                status=500,
                )
    return response

@app.route('/set_fault_rate', methods=['POST'])
def set_fault_rate():
    if request.method in ['POST']:
        fault_rate = request.json['fault_rate']
        secondary_node.set_fault_rate(fault_rate)
        return make_response(f'Node #{secondary_node.id} fault rate set to {fault_rate}', 200)
    else:
        return make_response('Unable to change fault rate', 500)

@app.route('/get_stored_mesages', methods=['GET'])
def get_stored_message():
    response = app.response_class(
        response=json.dumps({'message_ids': [message.id for message in secondary_node.messages]}),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    secondary_node = SecondaryNode(sys.argv[1])
    # app.run(host='0.0.0.0', threaded=True)
    
    app.run(host='localhost', port=str(sys.argv[2]), threaded=True, debug=False)
    