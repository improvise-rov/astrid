from src.common.net.worker import _Packet
"""
v2 of networking code. 

packet types

""" 

NONE:               _Packet = 0, None    # in case of emergency! blank packets shouldn't do anything, and they would resolve to 0.
MSG:                _Packet = 1, None    # used mostly just for testing. doesnt do anything
DISCONNECT:         _Packet = 2, None    # sent to opposite client when one tries to disconnect. tells the other to send an acknowledgement
DISCONNECT_ACK:     _Packet = 3, None    # sent back after PACKET_DISCONNECT to acknowledge the disconnect
CAMERA:             _Packet = 4, None    # sent with a camera frame.
CONTROL:            _Packet = 5, ">6f3i" # sent with information about control values
ENABLE_CORRECTION:  _Packet = 6, None    # when received, enables correction
DISABLE_CORRECTION: _Packet = 7, None    # when received, disables correction
STOP_SERVER:        _Packet = 8, None    # when received, server kills itself nicely
CONNECT:            _Packet = 9, None    # when received by the server, it remembers the source ip as where to send information. it also sends
CONNECT_ACK:        _Packet =10, None    # when received by the client, it marks itself connected