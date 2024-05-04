from typing import Optional, Sequence, Union

from litestar import Response

from sshared.api.structs import ErrorStruct, ResponseStruct


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


def fail(*, status_code: int, message: str, details: str) -> Response:
    return Response(
        ErrorStruct(message=message, details=details), status_code=status_code
    )
