

"""
Shared Constants among other files in the program.

Don't import anything here, we dont want cyclic imports.
"""

# window
WINDOW_TITLE: str = "impROVise: Astrid Client v2"
WINDOW_WIDTH: int = 1280 //2
WINDOW_HEIGHT: int = 720 //2

# ascii art
IMPROVISE_ASCII_ART_STRING: str = """  _                 ____   _____     ___          
 (_)_ __ ___  _ __ |  _ \\ / _ \\ \\   / (_)___  ___ 
 | | '_ ` _ \\| '_ \\| |_) | | | \\ \\ / /| / __|/ _ \\
 | | | | | | | |_) |  _ <| |_| |\\ V / | \\__ \\  __/
 |_|_| |_| |_| .__/|_| \\_\\\\___/  \\_/  |_|___/\\___|
             |_|                                  """

# pin numbers
PIN_ESC_MOTOR_FRONT_LEFT: int   = -1
PIN_ESC_MOTOR_FRONT_RIGHT: int  = -1
PIN_ESC_MOTOR_BACK_LEFT: int    = -1
PIN_ESC_MOTOR_BACK_RIGHT: int   = -1
PIN_ESC_MOTOR_TOP_LEFT: int     = -1
PIN_ESC_MOTOR_TOP_RIGHT: int    = -1
PIN_SERVO_CLAW_ROTATION: int    = -1
PIN_SERVO_CLAW_GRIP: int        = -1
PIN_SERVO_CAMERA_ANGLE: int     = -1

# physical quantities
ESC_PWM_MOTOR_SPEED_NEUTRAL: int = 127
ESC_PWM_MOTOR_SPEED_FULL_REVERSE: int = 0
ESC_PWM_MOTOR_SPEED_FULL_FORWARD: int = 255
CAMERA_ANGLE_NEUTRAL: int = 0
CLAW_ROTATION_ANGLE_NEUTRAL: int = 0
CLAW_OPEN: int = 0

# opencv
CAMERA_JPEG_COMPRESSION_VALUE: int = 65

# competition
POOL_RUN_TIME_SECONDS: int = 15 * 60