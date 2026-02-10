

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

# i2c address numbers
ADDRESS_ESC_MOTOR_FRONT_LEFT: int   = 0
ADDRESS_ESC_MOTOR_FRONT_RIGHT: int  = 1
ADDRESS_ESC_MOTOR_BACK_LEFT: int    = 2
ADDRESS_ESC_MOTOR_BACK_RIGHT: int   = 3
ADDRESS_ESC_MOTOR_TOP_LEFT: int     = 4
ADDRESS_ESC_MOTOR_TOP_RIGHT: int    = 5
ADDRESS_SERVO_CLAW_WRIST: int       = 10
ADDRESS_SERVO_CLAW_GRIP: int        = 11
ADDRESS_SERVO_CAMERA_ANGLE: int     = 15

# ^^^^^^^^^^^^^^
# the addresses are in 4 groups of 4.
#
# towards motors <- 0123 4567 8911 1111 -> towards camera
#                               01 2345
#
# if i address the motors nearest the physical end where the ESCs are, the wiring is neater
# likewise, if i put the camera servo at the opposite end and the tool servos somewhere in the middle
# 



# byte quantities
ESC_BYTE_MOTOR_SPEED_FULL_REVERSE: int = 0
ESC_BYTE_MOTOR_SPEED_NEUTRAL: int = 127
ESC_BYTE_MOTOR_SPEED_FULL_FORWARD: int = 255
SERVO_BYTE_COUNTER_CLOCKWISE: int = 0
SERVO_BYTE_CENTERED: int = 127
SERVO_BYTE_CLOCKWISE: int = 255

# physical quantities
I2C_ADDRESS_COUNT: int = 16 # the breakout board has 16 channels. we only use 9
SERVO_ANGLE_MIN: int = 0
SERVO_ANGLE_NEUTRAL: int = 90
SERVO_ANGLE_MAX: int = 180
MOTOR_THROTTLE_NEGATIVE: float = -1.0
MOTOR_THROTTLE_NEUTRAL: float = 0.0
MOTOR_THROTTLE_POSITIVE: float = 1.0

# pwm values ; now unneeded! but i left them here for reference in case they are needed at some point
PWM_REVERSE_ESC_MICROSECONDS: int = 1100
PWM_INITIALISE_ESC_MICROSECONDS: int = 1500
PWM_FORWARD_ESC_MICROSECONDS: int = 1900
PWM_SERVO_MINIMUM: int = 1000
PWM_SERVO_NEUTRAL: int = 1500
PWM_SERVO_MAXIMUM: int = 2000

# opencv
CAMERA_ID: int = 0
CAMERA_JPEG_COMPRESSION_VALUE: int = 65

# competition
POOL_RUN_TIME_SECONDS: int = 15 * 60