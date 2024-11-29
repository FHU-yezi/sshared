from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Response

from .structs import ErrorStruct, ResponseStruct

if TYPE_CHECKING:
    from collections.abc import Sequence


def success(
    data: ResponseStruct | Sequence[ResponseStruct] | None = None,
    /,
    *,
    status_code: int | None = None,
) -> Response:
    if data:
        if isinstance(data, ResponseStruct):
            data.validate()
        if isinstance(data, (list, tuple, set)):
            for item in data:
                item.validate()

    return Response(data, status_code=status_code)


def error(*, status_code: int, message: str, details: str | None = None) -> Response:
    return Response(
        ErrorStruct(message=message, details=details), status_code=status_code
    )
