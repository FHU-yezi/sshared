from typing import Callable, Union

from msgspec import Struct


class RetryEvent(Struct, frozen=True, eq=False, kw_only=True, gc=False):
    attempts: int
    delay: Union[int, float]
    func: Callable
    exception: Exception
