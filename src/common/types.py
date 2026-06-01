import typing

type _MotorKey = typing.Literal[
        'left_front', 'right_front',
        'left_top', 'right_top',
        'left_back', 'right_back'
        ]
    
type _ServoKey = typing.Literal[
    'camera_angle', 'tool_ver', 'tool_hor'
]

type _MotorOrServo = _MotorKey | _ServoKey


type _InputMethod = typing.Literal['gamepad', 'thrustmaster']