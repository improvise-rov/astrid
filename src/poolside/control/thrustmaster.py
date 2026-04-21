from __future__ import annotations
import typing
import pygame
from pygame.joystick import JoystickType

from src.common import types
from src.common import rovmath
from src.poolside.control.controller import AbstractController


type _ThrustmasterKey = typing.Literal[
    'none',
    
    'stick_forward',
    'stick_back',
    'stick_left',
    'stick_right',
    'stick_twist_cw',
    'stick_twist_ccw',
    'stick_x', # axis
    'stick_y', # axis
    'stick_twist', # axis
    
    'rudder_left',
    'rudder_right',
    'rudder', # axis
    
    'throttle_forward',
    'throttle_backward',
    'throttle', # axis

    'nib_up',
    'nib_down',
    'nib_left',
    'nib_right',
    'nib_x', # axis
    'nib_y', # axis

    'trigger',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '10',
    'se',
    'st',
]

class Thrustmaster(AbstractController[_ThrustmasterKey]):
    """
    _(Quite possibly the worst named object of all time)_\n\n

    interface for the flight stick control. hardcoded to work with what we (impROVise) have
    """
    DEVICE_GUID: str = "" # i need a way for the existing code to know that ive connected the thrustmaster. i can identify it by the guid

    KEY_NONE: _ThrustmasterKey = 'none'

    KEY_STICK_FORWARD: _ThrustmasterKey = 'stick_forward'
    KEY_STICK_BACKWARD: _ThrustmasterKey = 'stick_back'
    KEY_STICK_LEFT: _ThrustmasterKey = 'stick_left'
    KEY_STICK_RIGHT: _ThrustmasterKey = 'stick_right'
    KEY_STICK_TWIST_CW: _ThrustmasterKey = 'stick_twist_cw'
    KEY_STICK_TWIST_CCW: _ThrustmasterKey = 'stick_twist_ccw'

    AXIS_STICK_X: _ThrustmasterKey = 'stick_x'
    AXIS_STICK_Y: _ThrustmasterKey = 'stick_y'
    AXIS_STICK_TWIST: _ThrustmasterKey = 'stick_twist'

    KEY_RUDDER_LEFT: _ThrustmasterKey = 'rudder_left'
    KEY_RUDDER_RIGHT: _ThrustmasterKey = 'rudder_right'

    AXIS_RUDDER: _ThrustmasterKey = 'rudder'

    KEY_THROTTLE_FORWARD: _ThrustmasterKey = 'throttle_forward'
    KEY_THROTTLE_BACKWARD: _ThrustmasterKey = 'throttle_backward'

    AXIS_THROTTLE: _ThrustmasterKey = 'throttle'

    KEY_NIB_UP: _ThrustmasterKey = 'nib_up'
    KEY_NIB_DOWN: _ThrustmasterKey = 'nib_down'
    KEY_NIB_LEFT: _ThrustmasterKey = 'nib_left'
    KEY_NIB_RIGHT: _ThrustmasterKey = 'nib_right'

    AXIS_NIB_X: _ThrustmasterKey = 'nib_x'
    AXIS_NIB_Y: _ThrustmasterKey = 'nib_y'

    BUTTON_TRIGGER: _ThrustmasterKey = 'trigger'
    BUTTON_2: _ThrustmasterKey = '2'
    BUTTON_3: _ThrustmasterKey = '3'
    BUTTON_4: _ThrustmasterKey = '4'
    BUTTON_5: _ThrustmasterKey = '5'
    BUTTON_6: _ThrustmasterKey = '6'
    BUTTON_7: _ThrustmasterKey = '7'
    BUTTON_8: _ThrustmasterKey = '8'
    BUTTON_9: _ThrustmasterKey = '9'
    BUTTON_10: _ThrustmasterKey = '10'
    BUTTON_SE: _ThrustmasterKey = 'se'
    BUTTON_ST: _ThrustmasterKey = 'st'


    def __init__(self, joystick: JoystickType) -> None:
        super().__init__(joystick, 'thrustmaster', {
            Thrustmaster.KEY_NONE:               lambda g: 0.0,

            Thrustmaster.KEY_STICK_FORWARD:      lambda g: 0.0,
            Thrustmaster.KEY_STICK_BACKWARD:     lambda g: 0.0,
            Thrustmaster.KEY_STICK_LEFT:         lambda g: 0.0,
            Thrustmaster.KEY_STICK_RIGHT:        lambda g: 0.0,

            Thrustmaster.KEY_STICK_TWIST_CW:     lambda g: 0.0,
            Thrustmaster.KEY_STICK_TWIST_CCW:    lambda g: 0.0,

            Thrustmaster.AXIS_STICK_X:           lambda g: g._get_axis(2),
            Thrustmaster.AXIS_STICK_Y:           lambda g: g._get_axis(3),
            Thrustmaster.AXIS_STICK_TWIST:       lambda g: 0.0,

            Thrustmaster.KEY_RUDDER_LEFT:        lambda g: 0.0,
            Thrustmaster.KEY_RUDDER_RIGHT:       lambda g: 0.0,

            Thrustmaster.AXIS_RUDDER:            lambda g: 0.0,

            Thrustmaster.KEY_THROTTLE_FORWARD:   lambda g: 0.0,
            Thrustmaster.KEY_THROTTLE_BACKWARD:  lambda g: 0.0,

            Thrustmaster.AXIS_THROTTLE:          lambda g: 0.0,

            Thrustmaster.KEY_NIB_UP:             lambda g: 0.0,
            Thrustmaster.KEY_NIB_DOWN:           lambda g: 0.0,
            Thrustmaster.KEY_NIB_LEFT:           lambda g: 0.0,
            Thrustmaster.KEY_NIB_RIGHT:          lambda g: 0.0,

            Thrustmaster.AXIS_NIB_X:             lambda g: 0.0,
            Thrustmaster.AXIS_NIB_Y:             lambda g: 0.0,
            
            Thrustmaster.BUTTON_TRIGGER:         lambda g: 0.0,
            Thrustmaster.BUTTON_2:               lambda g: 0.0,
            Thrustmaster.BUTTON_3:               lambda g: 0.0,
            Thrustmaster.BUTTON_4:               lambda g: 0.0,
            Thrustmaster.BUTTON_5:               lambda g: 0.0,
            Thrustmaster.BUTTON_6:               lambda g: 0.0,
            Thrustmaster.BUTTON_7:               lambda g: 0.0,
            Thrustmaster.BUTTON_8:               lambda g: 0.0,
            Thrustmaster.BUTTON_9:               lambda g: 0.0,
            Thrustmaster.BUTTON_10:              lambda g: 0.0,
            Thrustmaster.BUTTON_SE:              lambda g: 0.0,
            Thrustmaster.BUTTON_ST:              lambda g: 0.0,
        })      
    
    