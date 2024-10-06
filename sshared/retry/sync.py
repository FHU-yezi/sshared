from functools import wraps
from time import sleep
from typing import Any, Callable, Optional, Union

from .event import RetryEvent


def retry(
    *,
    attempts: int = 3,
    delay: Union[int, float, Callable[[int], Union[int, float]]] = 3,
    exceptions: Union[type[Exception], tuple[type[Exception], ...]] = (Exception,),
    on_retry: Optional[Callable[[RetryEvent], None]] = None,
) -> Callable:
    def outer(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            if attempts <= 0:
                raise ValueError("max_tries 必须大于 0")

            current_attempt = 1
            while current_attempt < attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:  # noqa: PERF203
                    current_delay = (
                        delay
                        if isinstance(delay, (int, float))
                        else delay(current_attempt)
                    )

                    if on_retry:
                        on_retry(
                            RetryEvent(
                                attempts=current_attempt,
                                delay=current_delay,
                                func=func,
                                exception=e,
                            ).validate()
                        )
                    sleep(current_delay)
                    current_attempt += 1

            # 此次尝试若依然产生异常则不会捕获，直接向上传递
            return func(*args, **kwargs)

        return inner

    return outer
