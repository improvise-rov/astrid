

"""
Shared Constants among other files in the program.

Don't import anything here, we dont want cyclic imports.
"""

# window
WINDOW_TITLE: str = "impROVise: Astrid Client v2"
WINDOW_WIDTH: int = 1920
WINDOW_HEIGHT: int = 1080
SCREEN_WIDTH: int = 1280 //2
SCREEN_HEIGHT: int = 720 //2

# ascii art
IMPROVISE_ASCII_ART_STRING: str = """  _                 ____   _____     ___          
 (_)_ __ ___  _ __ |  _ \\ / _ \\ \\   / (_)___  ___ 
 | | '_ ` _ \\| '_ \\| |_) | | | \\ \\ / /| / __|/ _ \\
 | | | | | | | |_) |  _ <| |_| |\\ V / | \\__ \\  __/
 |_|_| |_| |_| .__/|_| \\_\\\\___/  \\_/  |_|___/\\___|
             |_|                                  """

# colors
SAFETY_ORANGE: int = 0xFF6700
GLAUCOUS: int = 0x6082B6

# i2c servo board address numbers
ADDRESS_ESC_MOTOR_FRONT_LEFT: int   = 0
ADDRESS_ESC_MOTOR_FRONT_RIGHT: int  = 1
ADDRESS_ESC_MOTOR_BACK_LEFT: int    = 2
ADDRESS_ESC_MOTOR_BACK_RIGHT: int   = 3
ADDRESS_ESC_MOTOR_TOP_LEFT: int     = 4
ADDRESS_ESC_MOTOR_TOP_RIGHT: int    = 5
ADDRESS_SERVO_TOOL_VER: int       = 10
ADDRESS_SERVO_TOOL_HOR: int        = 11
ADDRESS_SERVO_CAMERA_ANGLE: int     = 15

# ^^^^^^^^^^^^^^
# the addresses (channels) are in 4 groups of 4.
#
# towards motors <- 0123 4567 8911 1111 -> towards camera
#                               01 2345
#
# (alternatively, 0 is leftmost when the pin header colours are the german flag but upside down) 
#
# if i address the motors nearest the physical end where the ESCs are, the wiring is neater
# likewise, if i put the camera servo at the opposite end and the tool servos somewhere in the middle
# 

# networking
PACKET_SIZE: int = 1024*16

# byte quantities
ESC_BYTE_MOTOR_SPEED_FULL_REVERSE: int = 0
ESC_BYTE_MOTOR_SPEED_NEUTRAL: int = 127
ESC_BYTE_MOTOR_SPEED_FULL_FORWARD: int = 255
SERVO_BYTE_COUNTER_CLOCKWISE: int = 0
SERVO_BYTE_CENTERED: int = 127
SERVO_BYTE_CLOCKWISE: int = 255

# physical quantities
SERVOBOARD_CHANNEL_COUNT: int = 16 # the breakout board has 16 channels. we only use 9
SERVO_ANGLE_MIN: int = 0
SERVO_ANGLE_NEUTRAL: int = 90
SERVO_ANGLE_MAX: int = 180
MOTOR_THROTTLE_NEGATIVE: float = -1.0 / 2 # limit power (prevent current brownout)
MOTOR_THROTTLE_NEUTRAL: float = 0.0
MOTOR_THROTTLE_POSITIVE: float = 1.0 / 2

# pwm values 
PWM_ESC_REVERSE: int = 1200
PWM_ESC_INITIALISE: int = 1600 # 100us higher than it should be but we ball
PWM_ESC_FORWARD: int = 2000
PWM_CAMERA_SERVO_MINIMUM: int = 1000
PWM_CAMERA_SERVO_NEUTRAL: int = 1500
PWM_CAMERA_SERVO_MAXIMUM: int = 2000
PWM_TOOL_SERVO_MINIMUM: int = 500
PWM_TOOL_SERVO_NEUTRAL: int = 1500
PWM_TOOL_SERVO_MAXIMUM: int = 2500
PWM_FREQUENCY: int = 50

# imu
IMU_I2C_ADDRESS: int = 0x00

# opencv
CAMERA_ID: int = 0
CAMERA_JPEG_COMPRESSION_VALUE: int = 35
CAMERA_ROTATE: int = 1 # 0 = 0 ; 1 = 90cw ; 2 = 90ccw ; 3 = 180

# competition
POOL_RUN_TIME_SECONDS: int = 15 * 60

# float
FLOAT_IP: str = "127.0.0.1"
FLOAT_PORT: int = 8090
FLOAT_PACKET_SIZE: int = 1024