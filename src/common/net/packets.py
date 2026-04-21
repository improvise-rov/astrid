from src.common.net.worker import _Packet
"""
v2 of networking code. 

packet types

""" 

NONE:               _Packet = 0, None    # in case of emergency! blank packets shouldn't do anything, and they would resolve to 0.
MSG:                _Packet = 1, None    # used mostly just for testing. doesnt do anything
CAMERA:             _Packet = 2, None    # sent with a camera frame.
CONTROL:            _Packet = 3, ">6f3i" # sent with information about control values
ENABLE_CORRECTION:  _Packet = 4, None    # when received, enables correction
DISABLE_CORRECTION: _Packet = 5, None    # when received, disables correction
KILL:        _Packet = 6, None    # when received, rov kills itself nicely
CONNECT:            _Packet = 7, None    # when received by the rov, it remembers the source ip as where to send information.
CONNECT_ACK:        _Packet = 8, None    # when received by the poolside, it marks itself connected