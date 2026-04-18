from __future__ import annotations
import pygame
import typing

from pygame.joystick import JoystickType

from src.client.control.controller import AbstractController


type _Key = typing.Literal[
        'none',
        
        'a',
        'b',
        'x',
        'y',

        'start',
        'home',
        'select',

        'lbumper',
        'rbumper',

        'lstick',
        'rstick',

        'lstick_up',
        'lstick_down',
        'lstick_left',
        'lstick_right',

        'rstick_up',
        'rstick_down',
        'rstick_left',
        'rstick_right',

        'dpad_up',
        'dpad_down',
        'dpad_left',
        'dpad_right',

        'ltrigger_digital',
        'rtrigger_digital',

        'ltrigger_analogue',
        'rtrigger_analogue',

        'lstick_x',
        'lstick_y',
        'rstick_x',
        'rstick_y',

        'dpad_x',
        'dpad_y',
    ]

class Gamepad(AbstractController[_Key]):
    """
    Acts more or less as a wrapper around pygame's joystick module.
    Mostly taken from the source code of VRÖÖM because it works and i didnt want to write it again :P

    Note to the poor, poor future developer:
    VRÖÖM is a game i, Fynn, am making. (slowly).

    there are a BUNCH of constants on this class, for every key.
    plus two things you can change if you like, `NINTENDOIFIED_MAPPING` and `STICK_AXIS_AS_DIGITAL_DEADZONE`.
    
    in this classes functions i use the word "fallback" alot. this is a bit misleading, since
    the keyboard fallback actually takes priority. why'd i do that? i dont know, i wrote this a while ago.
    i guess i just forgot what fallback means; refactor it if you like, idc

    anyway also "deadzone" refers to the absolute value in which if the axis value is within, it is ignored
    for a stick, that can be assumed to be a radius of a circle around the stick center that always returns 0
    this is a common form of error correction that can account for slight imprecisions in older sticks
    """


    NONE: _Key = 'none'

    KEY_A: _Key = 'a'
    KEY_B: _Key = 'b'
    KEY_X: _Key = 'x'
    KEY_Y: _Key = 'y'
    KEY_START: _Key = 'start'
    KEY_HOME: _Key = 'home'
    KEY_SELECT: _Key = 'select'
    KEY_LEFT_BUMPER: _Key = 'lbumper'
    KEY_RIGHT_BUMPER: _Key = 'rbumper'
    KEY_LEFT_STICK: _Key = 'lstick'
    KEY_RIGHT_STICK: _Key = 'rstick'
    KEY_LEFT_STICK_UP: _Key = 'lstick_up'
    KEY_LEFT_STICK_DOWN: _Key = 'lstick_down'
    KEY_LEFT_STICK_LEFT: _Key = 'lstick_left'
    KEY_LEFT_STICK_RIGHT: _Key = 'lstick_right'
    KEY_RIGHT_STICK_UP: _Key = 'rstick_up'
    KEY_RIGHT_STICK_DOWN: _Key = 'rstick_down'
    KEY_RIGHT_STICK_LEFT: _Key = 'rstick_left'
    KEY_RIGHT_STICK_RIGHT: _Key = 'rstick_right'
    KEY_DPAD_UP: _Key = 'dpad_up'
    KEY_DPAD_DOWN: _Key = 'dpad_down'
    KEY_DPAD_LEFT: _Key = 'dpad_left'
    KEY_DPAD_RIGHT: _Key = 'dpad_right'
    KEY_LEFT_TRIGGER_DIGITAL: _Key = 'ltrigger_digital'
    KEY_RIGHT_TRIGGER_DIGITAL: _Key = 'rtrigger_digital'

    AXIS_LEFT_TRIGGER_ANALOGUE: _Key = 'ltrigger_analogue'
    AXIS_RIGHT_TRIGGER_ANALOGUE: _Key = 'rtrigger_analogue'
    AXIS_LEFT_STICK_X: _Key = 'lstick_x'
    AXIS_LEFT_STICK_Y: _Key = 'lstick_y'
    AXIS_RIGHT_STICK_X: _Key = 'rstick_x'
    AXIS_RIGHT_STICK_Y: _Key = 'rstick_y' # there was a bug here. i microwaved it
    AXIS_DPAD_X: _Key = 'dpad_x'
    AXIS_DPAD_Y: _Key = 'dpad_y'

    LEFT_STICK: tuple[_Key, _Key] = (AXIS_LEFT_STICK_X, AXIS_LEFT_STICK_Y)
    RIGHT_STICK: tuple[_Key, _Key] = (AXIS_RIGHT_STICK_X, AXIS_RIGHT_STICK_Y)
    DPAD: tuple[_Key, _Key] = (AXIS_DPAD_X, AXIS_DPAD_Y)

    
    def __init__(self, joystick: JoystickType) -> None:
        self.nintendoified_mapping = False
        super().__init__(joystick, 'gamepad', { # based off an xbox controller even though i have an 8bitdo
            Gamepad.NONE:                           lambda g: 0.0,
            
            Gamepad.KEY_A:                          lambda g: g._get_button(1) if g.nintendoified_mapping else g._get_button(0),
            Gamepad.KEY_B:                          lambda g: g._get_button(0) if g.nintendoified_mapping else g._get_button(1),
            Gamepad.KEY_X:                          lambda g: g._get_button(3) if g.nintendoified_mapping else g._get_button(2),
            Gamepad.KEY_Y:                          lambda g: g._get_button(2) if g.nintendoified_mapping else g._get_button(3),

            Gamepad.KEY_START:                      lambda g: g._get_button(7),
            Gamepad.KEY_HOME:                       lambda g: g._get_button(10),
            Gamepad.KEY_SELECT:                     lambda g: g._get_button(6),

            Gamepad.KEY_LEFT_BUMPER:                lambda g: g._get_button(4),
            Gamepad.KEY_RIGHT_BUMPER:               lambda g: g._get_button(5),

            Gamepad.KEY_LEFT_STICK:                 lambda g: g._get_button(8),
            Gamepad.KEY_RIGHT_STICK:                lambda g: g._get_button(9),
            
            Gamepad.KEY_LEFT_STICK_UP:              lambda g: g._get_axis(1) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            Gamepad.KEY_LEFT_STICK_DOWN:            lambda g: g._get_axis(1) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            Gamepad.KEY_LEFT_STICK_LEFT:            lambda g: g._get_axis(0) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            Gamepad.KEY_LEFT_STICK_RIGHT:           lambda g: g._get_axis(0) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,

            Gamepad.KEY_RIGHT_STICK_UP:             lambda g: g._get_axis(3) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            Gamepad.KEY_RIGHT_STICK_DOWN:           lambda g: g._get_axis(3) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            Gamepad.KEY_RIGHT_STICK_LEFT:           lambda g: g._get_axis(2) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            Gamepad.KEY_RIGHT_STICK_RIGHT:          lambda g: g._get_axis(2) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,

            Gamepad.KEY_DPAD_UP:                    lambda g: g._get_dpad(0)[1] == 1,
            Gamepad.KEY_DPAD_DOWN:                  lambda g: g._get_dpad(0)[1] == -1,
            Gamepad.KEY_DPAD_LEFT:                  lambda g: g._get_dpad(0)[0] == -1,
            Gamepad.KEY_DPAD_RIGHT:                 lambda g: g._get_dpad(0)[0] == 1,

            Gamepad.AXIS_LEFT_TRIGGER_ANALOGUE:     lambda g: g._get_axis(4),
            Gamepad.AXIS_RIGHT_TRIGGER_ANALOGUE:    lambda g: g._get_axis(5),

            Gamepad.KEY_LEFT_TRIGGER_DIGITAL:       lambda g: g._get_axis(4) > -1,
            Gamepad.KEY_RIGHT_TRIGGER_DIGITAL:      lambda g: g._get_axis(5) > -1,

            Gamepad.AXIS_LEFT_STICK_X:              lambda g: g._get_axis(0),
            Gamepad.AXIS_LEFT_STICK_Y:              lambda g: g._get_axis(1),

            Gamepad.AXIS_RIGHT_STICK_X:             lambda g: g._get_axis(2),
            Gamepad.AXIS_RIGHT_STICK_Y:             lambda g: g._get_axis(3),

            Gamepad.AXIS_DPAD_X:                    lambda g: float(g._get_dpad(0)[0]),
            Gamepad.AXIS_DPAD_Y:                    lambda g: float(g._get_dpad(0)[1]),
        })


    