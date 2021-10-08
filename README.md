# Replicated log
This is a Recplicated log task realization from DE UCU program
## Setting up
This package among others use flask web-server framework
To install all required packages run
pip3 install -r requirements.txt
## Running
### Primary node
To run Primary node primary_node.py should be used

python3 primary_node.py -P 10000 -p1 10001 -p2 10002

-P - port to run primary node
-p1 - port on which first secondary node is running
-p2 - port on which second secondary node is running
### Secondary node
To run Primary node primary_node.py should be used

python3 secondary_node.py -P 10001

-P - port to run secondary node