from __future__ import annotations

from typing import Literal, Union

ExtraType = Union[
    bool,
    int,
    float,
    str,
    None,
]


LogLevelType = Literal["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
