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

Returns a list of messages in sorted order that had been delivered with corresponding write consern

#### POST /add_secondary

{
    "id": 203,
    "host": "localhost",
    "port": "5003"
}

Adding secondary node to the cluster in run time with specified parameters

Returns success message

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

#### POST /set_fault_rate

{
    "fault_rate": 10
}

Sets fault rate of /add_message request to ***fault_rate*** value. If fault_rate > 0.0 secondary returns error messages with fault_rate probability

Returns confirmation message