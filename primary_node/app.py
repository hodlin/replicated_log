import json
import logging
from flask import Flask
from flask import request, make_response
from model import PrimaryNode

primary_node = PrimaryNode()

app = Flask(__name__)

logging.basicConfig(filename='primary_node.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s primary_node : %(message)s')

primary_node = PrimaryNode(logger=app.logger)

@app.route('/')
def index():
    return f'<p>Index page.</p>'

@app.route('/add_secondary', methods=['POST'])
def add_secondary_node():
    primary_node.add_secondary_node(request.json["id"], request.json["host"], request.json["port"])
    response = make_response(f'OK!', 200)
    return response

@app.route('/add_message', methods=['POST'])
def add_message():
    if request.method == 'POST':
        message_data = request.json
        write_concern = message_data['w']
        message = message_data['message']
        id = primary_node.add_message(message, write_concern)
        if id:
            response = make_response(f'Message saved with id {id}', 200)
        else:
            response = make_response(f'There is no quorum in cluster. Your message could not be stored. Try again later.', 200)
    else:
        response = make_response("Bad request", 400)
    return response

@app.route('/list_messages', methods=['GET'])
def list_message():
    messages_to_display = primary_node.messages_to_display()
    response = app.response_class(
        response=json.dumps({'messages': [message.to_json() for message in messages_to_display]}),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    primary_node.add_secondary_node(201, 'secondary_1', '5000')
    primary_node.add_secondary_node(202, 'secondary_2', '5000')
    app.run(host='0.0.0.0', threaded=True)

    # primary_node.add_secondary_node(201, 'localhost', '5001')
    # primary_node.add_secondary_node(202, 'localhost', '5002')
    # app.run(host='localhost', port='5000', threaded=True, debug=False)