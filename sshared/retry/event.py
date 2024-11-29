from __future__ import annotations

from typing import Callable

from sshared.strict_struct import (
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    StrictFrozenStruct,
)


class RetryEvent(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    attempts: PositiveInt
    delay: NonNegativeInt | NonNegativeFloat
    func: Callable
    exception: Exception
