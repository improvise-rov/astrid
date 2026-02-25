import typing
import pygame
import struct
from src.common import packets
from src.common.network import Netsock
from src.common.rovmath import RovMath
from src.client.gamepad import GamepadManager



class RovInterface():
    """
    General "orchestrator" class for the entire ROV control system.

    This class, being "topside" (that is, NOT part of the code that runs onboard the ROV) is more or less an interface to the ROV.
    """
    
    type _MotorKey = typing.Literal['lf', 'rf', 'lt', 'rt', 'lb', 'rb', 'ca', 'tw', 'tg']

    def __init__(self, net: Netsock, gamepad_manager: GamepadManager) -> None:
        self.net = net
        self.gamepad_manager = gamepad_manager

        self.motors: dict[RovInterface._MotorKey, RovMath.Number] = {
            'lf': 0, # front left
            'rf': 0, # front right
            'lt': 0, # top left
            'rt': 0, # top right
            'lb': 0, # back left
            'rb': 0, # back right

            'ca': 0.0, # camera angle
            'tw': 0.0, # tool wrist
            'tg': 0.0, # tool grip
        }

        self.camera_angle_speed = 0.001
        self.wrist_rotate_speed = 0.01
        self.motor_smoothing = 0.01

        self.correction_enabled = True # if true, the ROV will attempt to stabilise itself using its IMU.


    def update(self, dt: float):

        # tick
        motor_tick: dict[RovInterface._MotorKey, RovMath.Number] = {
            'lf': 0, # front left
            'rf': 0, # front right
            'lt': 0, # top left
            'rt': 0, # top right
            'lb': 0, # back left
            'rb': 0, # back right
        }

        
        # calculate speeds
        if self.gamepad_manager.has():
            gp = self.gamepad_manager.fetch_first()

            camera_angle_change = gp.read_axis(self.gamepad_manager.keymap_translate('axis.camera_angle_change'))
            tool_grip = gp.read_axis(self.gamepad_manager.keymap_translate('axis.tool_grip'))
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

            motor_tick['lf'] = RovMath.clamp(-1.0, 1.0, -rotate - strafe + forward )
            motor_tick['rf'] = RovMath.clamp(-1.0, 1.0,  rotate + strafe + forward )
            motor_tick['lt'] = RovMath.clamp(-1.0, 1.0,  elevate                   )
            motor_tick['rt'] = RovMath.clamp(-1.0, 1.0,  elevate                   )
            motor_tick['lb'] = RovMath.clamp(-1.0, 1.0,  rotate - strafe - forward )
            motor_tick['rb'] = RovMath.clamp(-1.0, 1.0, -rotate + strafe - forward )

            # TODO test that this is the right configuration lol


            self.motors['ca'] = RovMath.clamp(-1, 1, self.motors['ca'] + camera_angle_change * self.camera_angle_speed)
            self.motors['tg'] = tool_grip
            self.motors['tw'] = RovMath.clamp(-1, 1, self.motors['tw'] + wrist * self.wrist_rotate_speed)


        # manual override
        keys = pygame.key.get_pressed()

        reverse = keys[pygame.K_KP_0]

        motor_tick['lf'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_7] else motor_tick['lf']
        motor_tick['rf'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_9] else motor_tick['rf']
        motor_tick['lt'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_4] else motor_tick['lt']
        motor_tick['rt'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_6] else motor_tick['rt']
        motor_tick['lb'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_1] else motor_tick['lb']
        motor_tick['rb'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_3] else motor_tick['rb']

        self.motors['lf'] = RovMath.move_toward(self.motors['lf'], motor_tick['lf'], self.motor_smoothing)
        self.motors['rf'] = RovMath.move_toward(self.motors['rf'], motor_tick['rf'], self.motor_smoothing)
        self.motors['lt'] = RovMath.move_toward(self.motors['lt'], motor_tick['lt'], self.motor_smoothing)
        self.motors['rt'] = RovMath.move_toward(self.motors['rt'], motor_tick['rt'], self.motor_smoothing)
        self.motors['lb'] = RovMath.move_toward(self.motors['lb'], motor_tick['lb'], self.motor_smoothing)
        self.motors['rb'] = RovMath.move_toward(self.motors['rb'], motor_tick['rb'], self.motor_smoothing)


        # send data
        self.net.send(packets.CONTROL, struct.pack(packets.FORMAT_PACKET_CONTROL,
                                                          self.motors['lf'],
                                                          self.motors['rf'],
                                                          self.motors['lt'],
                                                          self.motors['rt'],
                                                          self.motors['lb'],
                                                          self.motors['rb'],

                                                          RovMath.servo_angle_to_byte(self.motors['ca']),
                                                          RovMath.servo_angle_to_byte(self.motors['tw']),
                                                          RovMath.servo_angle_to_byte(self.motors['tg']),
                                                          ))
        
