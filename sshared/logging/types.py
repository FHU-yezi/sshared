from enum import Enum
from typing import Union

ExtraType = Union[
    bool,
    int,
    float,
    str,
    None,
]


class LogLevelEnum(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
