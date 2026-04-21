from __future__ import annotations
import pygame
import json

from src.poolside.logger import Logger
from src.poolside.callback import Callback
from src.poolside.control.controller import AbstractController
from src.poolside.control.gamepad import Gamepad
from src.poolside.control.thrustmaster import Thrustmaster

class ControllerManager():
    """
    Manager over control methods. Keeps track of several controllers that are connected, 
    but you probably only want the first. Use `GamepadManager#fetch_first()` for that.
    """

    def __init__(self, default_gamepads_nintendoified: bool = False) -> None:
        self.controllers: dict[int, AbstractController] = {}

        self.mappings: dict[str, dict[str, str]] = {}
        self.always_gamepad = False
        self.default_gamepads_nintendoified = default_gamepads_nintendoified

        Callback.add_listener(pygame.JOYDEVICEADDED, self._device_connect)
        Callback.add_listener(pygame.JOYDEVICEREMOVED, self._device_remove)

    def has(self) -> bool:
        """
        if `True`, there is AT LEAST one gamepad attached.
        """
        return len(self.controllers) > 0

    def fetch_first(self) -> AbstractController:
        """
        Get the first gamepad attached. This code is ass.

        Also it throws an error if there aren't any. Check `ControllerManager#has()` first.
        """
        for value in self.controllers.values():
            return value
        raise RuntimeError("Tried to fetch gamepad when none was available")

    def load_mappings(self, path: str):
        """
        I use a "keymap" system for assigning keys. 
        This lets you assign names to keys dependent on what they are doing.
        `path` is a path to a JSON file defining the names and assigning them keys. For example:

        ```
        {
            "gamepad": {
                "move": "lstick",
                "jump": "a",
                "some_other_key_i_dont_know": "none"
            },
            "some_other_input_method": {
                "move": "key",
                "jump": "key2",
            }
        }
        ```

        This function just loads that file and lets you use `ControllerManager#keymap_translate()`, which
        gets the actual keys from these names.

        """
        with open(path, 'r') as f:
            self.mappings = json.load(f)

    def _device_connect(self, event: pygame.Event):
        """
        internal event callback to track device connects
        """
        id: int = event.device_index

        joystick = pygame.Joystick(id)
        instance_id = joystick.get_instance_id()
        guid = joystick.get_guid()

        if guid == Thrustmaster.DEVICE_GUID and not self.always_gamepad:
            self.controllers[instance_id] = Thrustmaster(joystick)
        else:
            gp = Gamepad(joystick)
            gp.nintendoified_mapping = self.default_gamepads_nintendoified
            self.controllers[instance_id] = gp

        self.controllers[instance_id].named_mappings = self.mappings
        

        Logger.log(f"Gamepad (id: {id}, instance: {instance_id}) connected!")
        print(f"guid: {guid}")

    def _device_remove(self, event: pygame.Event):
        """
        internal event callback to track device disconnects
        """
        id: int = event.instance_id
        if id in self.controllers:
            Logger.log(f"Gamepad (instance: {id}) disconnected!")
            self.controllers[id].destroy()
            del self.controllers[id]
