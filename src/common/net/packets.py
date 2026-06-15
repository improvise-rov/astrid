from src.common.net.worker import _Packet
"""
v2 of networking code. 

packet types

""" 

NONE:               _Packet = 0, None    # in case of emergency! blank packets shouldn't do anything, and they would resolve to 0.
MSG_ROV2POOLSIDE:   _Packet = 1, ">1024p"# logs upto 1kb
CAMERA:             _Packet = 2, None    # sent with a camera frame.
CONTROL:            _Packet = 3, ">6f3i" # sent with information about control values
ENABLE_CORRECTION:  _Packet = 4, None    # when received, enables correction
DISABLE_CORRECTION: _Packet = 5, None    # when received, disables correction
KILL:               _Packet = 6, None    # when received, rov kills itself nicely
SYNC_CAMERA:        _Packet = 7, ">?"    # when received, rov syncs camera state
REQ_SYNC_CAMERA:    _Packet = 7, None    # when received, camera state will be synced