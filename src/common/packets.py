

"""
Simple identifier constants for packet types. They're just integers..
"""

PACKET_NONE: int = 0 # in case of emergency! blank packets shouldn't do anything, and they would resolve to 0.

PACKET_MSG: int = 1
PACKET_DISCONNECT: int = 2
PACKET_DISCONNECT_ACK: int = 3
PACKET_CAMERA: int = 4
PACKET_CONTROL: int = 5

# the following are format strings for struct library
FORMAT_PACKET_CONTROL: str = "iiiiiiiii"