from __future__ import annotations
import pygame
import typing
import json

from src.client.logger import Logger
from src.client.callback import Callback

class GamepadManager():
    def __init__(self) -> None:
        self.gamepads: dict[int, Gamepad] = {}

        self.mappings: dict[str, str] = {}

        Callback.add_listener(pygame.JOYDEVICEADDED, self._device_connect)
        Callback.add_listener(pygame.JOYDEVICEREMOVED, self._device_remove)

    def has(self) -> bool:
        return len(self.gamepads) > 0

    def fetch_first(self) -> Gamepad:
        for value in self.gamepads.values():
            return value
        raise RuntimeError("Tried to fetch gamepad when none was available")
    
    def keymap_translate(self, mapping_key: str) -> str:
        return self.mappings.get(mapping_key, Gamepad.NONE)

    def load_mappings(self, path: str):
        with open(path, 'r') as f:
            self.mappings = json.load(f)

    def _device_connect(self, event: pygame.Event):
        id: int = event.device_index

        joystick = pygame.Joystick(id)
        instance_id = joystick.get_instance_id()
        self.gamepads[instance_id] = Gamepad(joystick)

        Logger.log(f"Gamepad (id: {id}, instance: {instance_id}) connected!")

    def _device_remove(self, event: pygame.Event):
        id: int = event.instance_id
        if id in self.gamepads:
            Logger.log(f"Gamepad (instance: {id}) disconnected!")
            self.gamepads[id].destroy()
            del self.gamepads[id]


class Gamepad():
    """
    Acts more or less as a wrapper around pygame's joystick module.
    Mostly taken from the source code of VRÖÖM because it works and i didnt want to write it again :P
    """

    NINTENDOIFIED_MAPPING: bool = False
    STICK_AXIS_AS_DIGITAL_DEADZONE: float = 0.1

    NONE: str = 'none'

    KEY_A: str = 'a'
    KEY_B: str = 'b'
    KEY_X: str = 'x'
    KEY_Y: str = 'y'
    KEY_START: str = 'start'
    KEY_HOME: str = 'home'
    KEY_SELECT: str = 'select'
    KEY_LEFT_BUMPER: str = 'lbumper'
    KEY_RIGHT_BUMPER: str = 'rbumper'
    KEY_LEFT_STICK: str = 'lstick'
    KEY_RIGHT_STICK: str = 'rstick'
    KEY_LEFT_STICK_UP: str = 'lstick_up'
    KEY_LEFT_STICK_DOWN: str = 'lstick_down'
    KEY_LEFT_STICK_LEFT: str = 'lstick_left'
    KEY_LEFT_STICK_RIGHT: str = 'lstick_right'
    KEY_RIGHT_STICK_UP: str = 'rstick_up'
    KEY_RIGHT_STICK_DOWN: str = 'rstick_down'
    KEY_RIGHT_STICK_LEFT: str = 'rstick_left'
    KEY_RIGHT_STICK_RIGHT: str = 'rstick_right'
    KEY_DPAD_UP: str = 'dpad_up'
    KEY_DPAD_DOWN: str = 'dpad_down'
    KEY_DPAD_LEFT: str = 'dpad_left'
    KEY_DPAD_RIGHT: str = 'dpad_right'
    KEY_LEFT_TRIGGER_DIGITAL: str = 'ltrigger_digital'
    KEY_RIGHT_TRIGGER_DIGITAL: str = 'rtrigger_digital'

    AXIS_LEFT_TRIGGER_ANALOGUE: str = 'ltrigger_analogue'
    AXIS_RIGHT_TRIGGER_ANALOGUE: str = 'rtrigger_analogue'
    AXIS_LEFT_STICK_X: str = 'lstick_x'
    AXIS_LEFT_STICK_Y: str = 'lstick_y'
    AXIS_RIGHT_STICK_X: str = 'rstick_x'
    AXIS_RIGHT_STICK_Y: str = 'rstick_y' # there was a bug here. i microwaved it
    AXIS_DPAD_X: str = 'dpad_x'
    AXIS_DPAD_Y: str = 'dpad_y'

    LEFT_STICK: tuple[str, str] = (AXIS_LEFT_STICK_X, AXIS_LEFT_STICK_Y)
    RIGHT_STICK: tuple[str, str] = (AXIS_RIGHT_STICK_X, AXIS_RIGHT_STICK_Y)
    DPAD: tuple[str, str] = (AXIS_DPAD_X, AXIS_DPAD_Y)

    MAPPING: dict[str, typing.Callable[[Gamepad], typing.Any]] = { # based off an xbox controller even though i have an 8bitdo
            NONE: lambda g: 0.0,

            KEY_A: lambda g: g._get_button(1) if Gamepad.NINTENDOIFIED_MAPPING else g._get_button(0),
            KEY_B: lambda g: g._get_button(0) if Gamepad.NINTENDOIFIED_MAPPING else g._get_button(1),
            KEY_X: lambda g: g._get_button(3) if Gamepad.NINTENDOIFIED_MAPPING else g._get_button(2),
            KEY_Y: lambda g: g._get_button(2) if Gamepad.NINTENDOIFIED_MAPPING else g._get_button(3),

            KEY_START: lambda g: g._get_button(7),
            KEY_HOME: lambda g: g._get_button(10),
            KEY_SELECT: lambda g: g._get_button(6),

            KEY_LEFT_BUMPER: lambda g: g._get_button(4),
            KEY_RIGHT_BUMPER: lambda g: g._get_button(5),

            KEY_LEFT_STICK: lambda g: g._get_button(8),
            KEY_RIGHT_STICK: lambda g: g._get_button(9),

            KEY_LEFT_STICK_UP: lambda g: g._get_axis(1) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            KEY_LEFT_STICK_DOWN: lambda g: g._get_axis(1) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            KEY_LEFT_STICK_LEFT: lambda g: g._get_axis(0) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            KEY_LEFT_STICK_RIGHT: lambda g: g._get_axis(0) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,

            KEY_RIGHT_STICK_UP: lambda g: g._get_axis(3) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            KEY_RIGHT_STICK_DOWN: lambda g: g._get_axis(3) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            KEY_RIGHT_STICK_LEFT: lambda g: g._get_axis(2) < -Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,
            KEY_RIGHT_STICK_RIGHT: lambda g: g._get_axis(2) > Gamepad.STICK_AXIS_AS_DIGITAL_DEADZONE,

            KEY_DPAD_UP: lambda g: g._get_dpad(0)[1] == 1,
            KEY_DPAD_DOWN: lambda g: g._get_dpad(0)[1] == -1,
            KEY_DPAD_LEFT: lambda g: g._get_dpad(0)[0] == -1,
            KEY_DPAD_RIGHT: lambda g: g._get_dpad(0)[0] == 1,

            AXIS_LEFT_TRIGGER_ANALOGUE: lambda g: g._get_axis(4),
            AXIS_RIGHT_TRIGGER_ANALOGUE: lambda g: g._get_axis(5),

            KEY_LEFT_TRIGGER_DIGITAL: lambda g: g._get_axis(4) > -1,
            KEY_RIGHT_TRIGGER_DIGITAL: lambda g: g._get_axis(5) > -1,

            AXIS_LEFT_STICK_X: lambda g: g._get_axis(0),
            AXIS_LEFT_STICK_Y: lambda g: g._get_axis(1),

            AXIS_RIGHT_STICK_X: lambda g: g._get_axis(2),
            AXIS_RIGHT_STICK_Y: lambda g: g._get_axis(3),

            AXIS_DPAD_X: lambda g: float(g._get_dpad(0)[0]),
            AXIS_DPAD_Y: lambda g: float(g._get_dpad(0)[1]),
        }

    def __init__(self, joystick: pygame.joystick.JoystickType) -> None:
        self.joystick = joystick
    
        self._last_states: dict[str, typing.Any] = {}
        self._states: dict[str, typing.Any] = {}

        self._fallback_keyboard_press_read = []
        self._fallback_keyboard_release_read = []
        self._fallback_keyboard_down_read = []

        self.poll_states()

  
    def _is_connected(self) -> bool:
        return self.joystick != None
    
    def _has_standard_min_standard_inputs(self) -> bool:
        return self._get_numbuttons() >= 11 and self._get_numaxes() >= 2 and self._get_numhats() >= 1
    
    def _is_connected_with_standard_inputs(self) -> bool:
        return self._is_connected() and self._has_standard_min_standard_inputs()

    def _get_pygame_joystick(self) -> pygame.joystick.JoystickType:
        if self.joystick:
            return self.joystick
        else:
            raise ConnectionError("Gamepad does not have a joystick attached (there probably arent any attached to the computer)")

    def _get_gamepad_name(self) -> str:
        if self.joystick:
            return self.joystick.get_name()
        else:
            return "Not Connected"
        
    def _get_numbuttons(self) -> int:
        if self.joystick:
            return self.joystick.get_numbuttons()
        else:
            return -1
        
    def _get_numaxes(self) -> int:
        if self.joystick:
            return self.joystick.get_numaxes()
        else:
            return -1
        
    def _get_numhats(self) -> int:
        if self.joystick:
            return self.joystick.get_numhats()
        else:
            return -1
    
    def _get_power_status(self) -> str:
        if self.joystick:
            return self.joystick.get_power_level()
        else:
            return 'disconnected'
    
    def _get_axis(self, axis: int) -> float:
        try:
            return self._get_pygame_joystick().get_axis(axis)
        except:
            return 0.0

    def _get_button(self, button: int) -> bool:
        try:
            return self._get_pygame_joystick().get_button(button) == 1
        except:
            return False
    
    def _get_dpad(self, dpad: int) -> tuple[float, float]:
        try:
            return self._get_pygame_joystick().get_hat(dpad)
        except:
            return (0, 0)
    
    ##
    
    def poll_states(self) -> bool:
        """
        Returns `True` if any gamepad state has changed since the last poll.\n
        Returns `False` if `self.joystick == None`.
        """

        self._fallback_keyboard_press_read = pygame.key.get_just_pressed()
        self._fallback_keyboard_release_read = pygame.key.get_just_released()
        self._fallback_keyboard_down_read = pygame.key.get_pressed()

        if self.joystick:
            self._last_states = self._states
            self._states = {}
            any_different = False
            for key in Gamepad.MAPPING:
                self._states[key] = Gamepad.MAPPING[key](self)
                if not any_different and key in self._last_states and self._states[key] != self._last_states[key]:
                    any_different = True

            return any_different

        return False

    ##

    def digital_down(self, *keys: str, keyboard_fallback: int = pygame.K_UNKNOWN) -> bool:
        if keyboard_fallback != pygame.K_UNKNOWN and self._fallback_keyboard_down_read[keyboard_fallback]:
            return True
        
        if self.joystick:
            for key in keys:
                if key not in self._states or not isinstance(self._states[key], bool): return False
                if self._states[key]:
                    return True
        
        return False

    
    def digital_pressed(self, *keys: str, keyboard_fallback: int = pygame.K_UNKNOWN) -> bool:
        if keyboard_fallback != pygame.K_UNKNOWN and self._fallback_keyboard_press_read[keyboard_fallback]:
            return True
        
        if self.joystick:
            for key in keys:
                if key not in self._states or not isinstance(self._states[key], bool): return False
                if key not in self._last_states or not isinstance(self._last_states[key], bool): return False
                if self._states[key] and not self._last_states[key]:
                    return True
        
        return False

    def digital_released(self, *keys: str, keyboard_fallback: int = pygame.K_UNKNOWN) -> bool:
        if keyboard_fallback != pygame.K_UNKNOWN and self._fallback_keyboard_release_read[keyboard_fallback]:
            return True
        
        if self.joystick:
            for key in keys:
                if key not in self._states or not isinstance(self._states[key], bool): return False
                if key not in self._last_states or not isinstance(self._last_states[key], bool): return False
                if not self._states[key] and self._last_states[key]:
                    return True
        
        return False
    
    def read_axis(self, key: str, deadzone: float = 0.1, *, keyboard_fallback_pos: int = pygame.K_UNKNOWN, keyboard_fallback_neg: int = pygame.K_UNKNOWN) -> float:
        
        fallback = 0.0
        if keyboard_fallback_pos != pygame.K_UNKNOWN and self._fallback_keyboard_release_read[keyboard_fallback_pos]:
            fallback += 1.0
        
        if keyboard_fallback_neg != pygame.K_UNKNOWN and self._fallback_keyboard_release_read[keyboard_fallback_neg]:
            fallback -= 1.0
        
        if self.joystick:
            if key not in self._states or not isinstance(self._states[key], float): return 0.0
            v = self._states[key]
            return v if abs(v) > deadzone else 0.0
        
        return fallback
    
    def read_vector(self, key_x: str, key_y: str, deadzone: float = 0.1, *, keyboard_fallback_x_pos: int = pygame.K_UNKNOWN, keyboard_fallback_x_neg: int = pygame.K_UNKNOWN, keyboard_fallback_y_pos: int = pygame.K_UNKNOWN, keyboard_fallback_y_neg: int = pygame.K_UNKNOWN) -> pygame.Vector2:
        
        x = 0
        y = 0

        x += 1 if keyboard_fallback_x_pos != pygame.K_UNKNOWN and self._fallback_keyboard_down_read[keyboard_fallback_x_pos] else 0
        x -= 1 if keyboard_fallback_x_neg != pygame.K_UNKNOWN and self._fallback_keyboard_down_read[keyboard_fallback_x_neg] else 0
        y += 1 if keyboard_fallback_y_pos != pygame.K_UNKNOWN and self._fallback_keyboard_down_read[keyboard_fallback_y_pos] else 0
        y -= 1 if keyboard_fallback_y_neg != pygame.K_UNKNOWN and self._fallback_keyboard_down_read[keyboard_fallback_y_neg] else 0

        if x != 0 or y != 0:
            return pygame.Vector2(x, y)

        if self.joystick:
            return pygame.Vector2(self.read_axis(key_x, deadzone), self.read_axis(key_y, deadzone))

        return pygame.Vector2(0, 0)
    
    def destroy(self):
        del self.joystick
    


    