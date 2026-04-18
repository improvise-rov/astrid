
"""
Packet identifiers for our float.
"""


NONE: int = 0 # in case of emergency!
START_NEW_PROFILE: int = 1 # tells morag to start a new profile (goes down, then back up)
RECEIVE_DATA_PLEASE: int = 1 # asks morag for its data from the last profile