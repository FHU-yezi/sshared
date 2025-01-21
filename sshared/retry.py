from __future__ import annotations

from asyncio import iscoroutinefunction
from asyncio import sleep as asleep
from collections.abc import Coroutine
from functools import wraps
from time import sleep
from typing import Any, Callable, TypeVar

from msgspec import Struct
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")
FuncType = Callable[P, R] | Callable[P, Coroutine[Any, Any, R]]


class RetryInfo(Struct, frozen=True, eq=False, gc=False):
    current_retries: int
    next_delay: float
    exception: Exception


def retry(
    *,
    retries: int,
    base_delay: float,
    exceptions: tuple[type[Exception], ...],
    on_exception: Callable[[RetryInfo], None] | None = None,
) -> Callable[[FuncType], FuncType]:
    def outer(func: FuncType) -> FuncType:
        if iscoroutinefunction(func):  # 异步函数

            @wraps(func)
            async def inner(*args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
                for current_retries in range(1, retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        next_delay = base_delay * current_retries  # 指数退避
                        if on_exception:
                            on_exception(
                                RetryInfo(
                                    current_retries=current_retries,
                                    next_delay=next_delay,
                                    exception=e,
                                )
                            )
                        await asleep(next_delay)

                return await func(*args, **kwargs)
        else:  # 同步函数

            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
                for current_retries in range(1, retries + 1):
                    try:
                        return func(*args, **kwargs)  # type: ignore
                    except exceptions as e:
                        next_delay = base_delay * current_retries  # 指数退避
                        if on_exception:
                            on_exception(
                                RetryInfo(
                                    current_retries=current_retries,
                                    next_delay=next_delay,
                                    exception=e,
                                )
                            )
                        sleep(base_delay * current_retries)  # 指数退避

                return func(*args, **kwargs)  # type: ignore

        return inner

    return outer
