from typing import Callable, Union

from sshared.strict_struct import (
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    StrictFrozenStruct,
)


class RetryEvent(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    attempts: PositiveInt
    delay: Union[NonNegativeInt, NonNegativeFloat]
    func: Callable
    exception: Exception
