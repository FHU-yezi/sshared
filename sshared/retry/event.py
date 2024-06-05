from typing import Callable, Union

from sshared.struct_constraints import (
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    ValidatableFrozenSturct,
)


class RetryEvent(ValidatableFrozenSturct, frozen=True, eq=False, gc=False):
    attempts: PositiveInt
    delay: Union[NonNegativeInt, NonNegativeFloat]
    func: Callable
    exception: Exception
