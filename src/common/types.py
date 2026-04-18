import typing

type _Motor = typing.Literal[
        'left_front', 'right_front',
        'left_top', 'right_top',
        'left_back', 'right_back'
        ]
    
type _Servo = typing.Literal[
    'camera_angle', 'tool_ver', 'tool_hor'
]

type _MotorOrServo = _Motor | _Servo