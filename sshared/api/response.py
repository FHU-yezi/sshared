from collections.abc import Sequence
from typing import Optional, Union

from litestar import Response

from .structs import ErrorStruct, ResponseStruct


def success(
    data: Optional[Union[ResponseStruct, Sequence[ResponseStruct]]] = None,
    /,
    *,
    status_code: Optional[int] = None,
) -> Response:
    if data:
        if isinstance(data, ResponseStruct):
            data.validate()
        if isinstance(data, (list, tuple, set)):
            for item in data:
                item.validate()

    return Response(data, status_code=status_code)


def error(*, status_code: int, message: str, details: Optional[str] = None) -> Response:
    return Response(
        ErrorStruct(message=message, details=details), status_code=status_code
    )
