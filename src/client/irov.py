import typing
import pygame
import struct
from src.common import packets
from src.common import consts
from src.common import types
from src.common.network import Netsock
from src.common.rovmath import RovMath
from src.client.gamepad import GamepadManager



class RovInterface():
    """
    General "orchestrator" class for the entire ROV control system.

    This class, being "topside" (that is, NOT part of the code that runs onboard the ROV) is more or less an interface to the ROV.
    """

    def __init__(self, net: Netsock, gamepad_manager: GamepadManager) -> None:
        self.net = net
        self.gamepad_manager = gamepad_manager

        self.motors: dict[types._Motor | types._Servo, RovMath.Number] = {
            'left_front': 0,
            'right_front': 0,
            'left_top': 0,
            'right_top': 0,
            'left_back': 0,
            'right_back': 0,

            'camera_angle': 0.0,
            'tool_ver': 0.0,
            'tool_hor': 0.0,
        }

        self.camera_angle_speed = 0.001
        self.wrist_rotate_speed = 0.01
        self.motor_smoothing = 0.01

        self.correction_enabled = True # if true, the ROV will attempt to stabilise itself using its IMU.


    def update(self, dt: float):

        # tick
        motor_tick: dict[types._Motor, RovMath.Number] = {
            'left_front': 0, # front left
            'right_front': 0, # front right
            'left_top': 0, # top left
            'right_top': 0, # top right
            'left_back': 0, # back left
            'right_back': 0, # back right
        }

        
        # calculate speeds
        if self.gamepad_manager.has():
            gp = self.gamepad_manager.fetch_first()

            camera_angle_change = gp.read_axis(self.gamepad_manager.keymap_translate('axis.camera_angle_change'))
            tool_grip_v = gp.read_axis(self.gamepad_manager.keymap_translate('axis.tool_grip'))
            tool_grip_h = gp.read_axis(self.gamepad_manager.keymap_translate('axis.tool_grip_h'))
            wrist = gp.digital_down(self.gamepad_manager.keymap_translate('digital.rotate_wrist.cw')) - gp.digital_down(self.gamepad_manager.keymap_translate('digital.rotate_wrist.ccw'))

            forward = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.forward'))
            strafe = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.strafe'))
            rotate = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.rotate'))
            elevate = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.elevate'))

            # calculate motors
            """
            rotate left             lf - rf   rotate right
            only used in elevation  lt - rt   only used in elevation
            rotate right            lb - rb   rotate left
            """

            motor_tick['left_front'] = RovMath.clamp(consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_POSITIVE, -rotate - strafe + forward )
            motor_tick['right_front'] = RovMath.clamp(consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_POSITIVE,  rotate + strafe + forward )
            motor_tick['left_top'] = RovMath.clamp(consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_POSITIVE,  elevate                   )
            motor_tick['right_top'] = RovMath.clamp(consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_POSITIVE,  elevate                   )
            motor_tick['left_back'] = RovMath.clamp(consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_POSITIVE,  rotate - strafe - forward )
            motor_tick['right_back'] = RovMath.clamp(consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_POSITIVE, -rotate + strafe - forward )

            # TODO test that this is the right configuration lol

            self.motors['camera_angle'] = RovMath.clamp(-1, 1, self.motors['camera_angle'] + camera_angle_change * self.camera_angle_speed)
            self.motors['tool_ver'] = tool_grip_v
            self.motors['tool_hor'] = tool_grip_h

        # manual override
        keys = pygame.key.get_pressed()

        reverse = keys[pygame.K_KP_0]

        motor_tick['left_front']  = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_7] else motor_tick['left_front']  
        motor_tick['right_front'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_9] else motor_tick['right_front'] 
        motor_tick['left_top']    = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_4] else motor_tick['left_top']    
        motor_tick['right_top']   = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_6] else motor_tick['right_top']   
        motor_tick['left_back']   = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_1] else motor_tick['left_back']   
        motor_tick['right_back']  = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_3] else motor_tick['right_back']  

        self.motors['left_front']   = RovMath.move_toward(self.motors['left_front']  , motor_tick['left_front']  , self.motor_smoothing)
        self.motors['right_front']  = RovMath.move_toward(self.motors['right_front'] , motor_tick['right_front'] , self.motor_smoothing)
        self.motors['left_top']     = RovMath.move_toward(self.motors['left_top']    , motor_tick['left_top']    , self.motor_smoothing)
        self.motors['right_top']    = RovMath.move_toward(self.motors['right_top']   , motor_tick['right_top']   , self.motor_smoothing)
        self.motors['left_back']    = RovMath.move_toward(self.motors['left_back']   , motor_tick['left_back']   , self.motor_smoothing)
        self.motors['right_back']   = RovMath.move_toward(self.motors['right_back']  , motor_tick['right_back']  , self.motor_smoothing)


        # send data
        self.net.send(packets.CONTROL, struct.pack(packets.FORMAT_PACKET_CONTROL,
                                                          self.motors['left_front']  ,
                                                          self.motors['right_front'] ,
                                                          self.motors['left_top']    ,
                                                          self.motors['right_top']   ,
                                                          self.motors['left_back']   ,
                                                          self.motors['right_back']  ,

                                                          RovMath.servo_angle_to_byte(self.motors['camera_angle']),
                                                          RovMath.servo_angle_to_byte(self.motors['tool_ver']),
                                                          RovMath.servo_angle_to_byte(self.motors['tool_hor']),
                                                          ))
        
