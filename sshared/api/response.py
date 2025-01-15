from __future__ import annotations

from collections.abc import Sequence

from litestar import Response

from .structs import ErrorStruct, ResponseStruct


def success(
    data: ResponseStruct | Sequence[ResponseStruct] | None = None,
    /,
    *,
    status_code: int | None = None,
) -> Response:
    if data:
        if isinstance(data, ResponseStruct):
            data.validate()
        else:
            for item in data:
                item.validate()

    return Response(data, status_code=status_code)


def error(*, status_code: int, message: str, details: str | None = None) -> Response:
    return Response(
        ErrorStruct(message=message, details=details), status_code=status_code
    )
