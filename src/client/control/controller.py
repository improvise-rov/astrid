from __future__ import annotations
import pygame
import typing

class AbstractController[_MappingKeyType]():
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

    
    STICK_AXIS_AS_DIGITAL_DEADZONE: float = 0.1

    
    def __init__(self, joystick: pygame.joystick.JoystickType, keys: dict[_MappingKeyType, typing.Callable[[typing.Self], typing.Any]]) -> None:
        self.joystick = joystick

        self.named_mappings: dict[str, _MappingKeyType] = {}

        self.keys = keys
    
        self._last_states: dict[_MappingKeyType, typing.Any] = {}
        self._states: dict[_MappingKeyType, typing.Any] = {}

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

    def keymap_translate(self, key: str, default: _MappingKeyType = None) -> _MappingKeyType:
        return self.named_mappings.get(key, default)
    
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
            for key in self.keys:
                self._states[key] = self.keys[key](self)
                if not any_different and key in self._last_states and self._states[key] != self._last_states[key]:
                    any_different = True

            return any_different

        return False

    ##

    def digital_down(self, *keys: _MappingKeyType, keyboard_fallback: int = pygame.K_UNKNOWN) -> bool:
        """
        Returns `True` if at least one of the specified keys (or fallback) is DOWN.
        """
        if keyboard_fallback != pygame.K_UNKNOWN and self._fallback_keyboard_down_read[keyboard_fallback]:
            return True
        
        if self.joystick:
            for key in keys:
                if key not in self._states or not isinstance(self._states[key], bool): return False
                if self._states[key]:
                    return True
        
        return False

    
    def digital_pressed(self, *keys: _MappingKeyType, keyboard_fallback: int = pygame.K_UNKNOWN) -> bool:
        """
        Returns `True` if at least one of the specified keys (or fallback) is DOWN, but WAS NOT the previous poll.
        """
        if keyboard_fallback != pygame.K_UNKNOWN and self._fallback_keyboard_press_read[keyboard_fallback]:
            return True
        
        if self.joystick:
            for key in keys:
                if key not in self._states or not isinstance(self._states[key], bool): return False
                if key not in self._last_states or not isinstance(self._last_states[key], bool): return False
                if self._states[key] and not self._last_states[key]:
                    return True
        
        return False

    def digital_released(self, *keys: _MappingKeyType, keyboard_fallback: int = pygame.K_UNKNOWN) -> bool:
        """
        Returns `True` if at least one of the specified keys (or fallback) is UP, but WAS NOT the previous frame.
        """
        if keyboard_fallback != pygame.K_UNKNOWN and self._fallback_keyboard_release_read[keyboard_fallback]:
            return True
        
        if self.joystick:
            for key in keys:
                if key not in self._states or not isinstance(self._states[key], bool): return False
                if key not in self._last_states or not isinstance(self._last_states[key], bool): return False
                if not self._states[key] and self._last_states[key]:
                    return True
        
        return False
    
    def read_axis(self, key: _MappingKeyType, deadzone: float = 0.1, *, keyboard_fallback_pos: int = pygame.K_UNKNOWN, keyboard_fallback_neg: int = pygame.K_UNKNOWN) -> float:
        """
        Returns the value of a given axial value.
        
        `_pos`: positive, `_neg`: negative
        """

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
    
    def read_vector(self, key_x: _MappingKeyType, key_y: _MappingKeyType, deadzone: float = 0.1, *, keyboard_fallback_x_pos: int = pygame.K_UNKNOWN, keyboard_fallback_x_neg: int = pygame.K_UNKNOWN, keyboard_fallback_y_pos: int = pygame.K_UNKNOWN, keyboard_fallback_y_neg: int = pygame.K_UNKNOWN) -> pygame.Vector2:
        """
        Returns a vector representing two axial values.
        
        `_pos`: positive, `_neg`: negative
        """

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
        """
        ya yeet the internal object out of existence GET OUTTA HEREEEEE
        """
        del self.joystick
    


    