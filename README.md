# Replicated log
This is a Recplicated log task realization from Distributed Systems course of Data Engineering 2021 program at UCU
## Setting up
This package among others use flask web-server framework set up with docker
There one primary node an two secondaries
To run everything up run docker-compose up

## Running
### Primary node
Primary node is run on 5000 port of localhost and has following interfaces:

#### POST /add_message

{
    "message": "Message text"
    "w": 1
}

Adding message with ***w*** write consern

Returns success message

#### GET /list_messages

Returns a list of messages in sorted order

### Secondary node
Secondary nodes are running on localhost's 5001 and 5002 ports and has following interfaces:

#### GET /list_messages

Returns a list of messages in sorted order. If any message is missed later messages won't be shown

#### POST /set_delay

{
    "delay": 10
}

Sets delay of internal /add_message request to ***delay*** seconds

Returns confirmation message