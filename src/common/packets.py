

"""
Simple identifier constants for packet types. They're just integers..
"""

NONE: int = 0 # in case of emergency! blank packets shouldn't do anything, and they would resolve to 0.

MSG: int = 1 # used mostly just for testing. doesnt do anything
DISCONNECT: int = 2 # sent to opposite client when one tries to disconnect. tells the other to send an acknowledgement
DISCONNECT_ACK: int = 3 # sent back after PACKET_DISCONNECT to acknowledge the disconnect
CAMERA: int = 4 # sent with a camera frame.
CONTROL: int = 5 # sent with information about control values
ENABLE_CORRECTION: int = 6 # when received, enables correction
DISABLE_CORRECTION: int = 7 # when received, disables correction
STOP_SERVER: int = 8 # when received, server kills itself nicely

# the following are format strings for struct library
# lf, rf, lt, rt, lb, rb, ca, tw, tg
FORMAT_PACKET_CONTROL: str = "ffffffiii"