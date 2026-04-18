
"""
Packet identifiers for our float.
"""


NONE: int = 0 # in case of emergency!
START_NEW_PROFILE: int = 1 # tells morag to start a new profile (goes down, then back up)
RECEIVE_DATA_PLEASE: int = 2 # asks morag for its data from the last profile
DATA_PAYLOAD: int = 3 # morag sends this along with big yummy scientfic data