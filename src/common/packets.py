

"""
Simple identifier constants for packet types. They're just integers..
"""

PACKET_NONE: int = 0 # in case of emergency! blank packets shouldn't do anything, and they would resolve to 0.

PACKET_MSG: int = 1 # used mostly just for testing. doesnt do anything
PACKET_DISCONNECT: int = 2 # sent to opposite client when one tries to disconnect. tells the other to send an acknowledgement
PACKET_DISCONNECT_ACK: int = 3 # sent back after PACKET_DISCONNECT to acknowledge the disconnect
PACKET_CAMERA: int = 4 # sent with a camera frame.
PACKET_CONTROL: int = 5 # sent with information about control values

# the following are format strings for struct library
FORMAT_PACKET_CONTROL: str = "iiiiiiiii"