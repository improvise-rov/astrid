

"""
Simple identifier constants for packet types. They're just integers..
"""

PACKET_NONE: int = 0 # in case of emergency! blank packets shouldn't do anything, and they would resolve to 0.

PACKET_C2S_HANDSHAKE: int = 1
PACKET_C2S_DISCONNECT: int = 2
PACKET_C2S_CONTROL: int = 3

PACKET_S2C_HANDSHAKE: int = 4
PACKET_S2C_DISCONNECT: int = 5
PACKET_S2C_CAMERA: int = 6