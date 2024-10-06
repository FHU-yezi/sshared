from typing import Any

from litestar import Request, Response
from litestar.exceptions import ValidationException
from litestar.exceptions.http_exceptions import (
    MethodNotAllowedException,
    NotFoundException,
)
from litestar.status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.types import ExceptionHandlersMap

from sshared.time import get_now_without_microsecond

from .response import error


def _generate_details_from_validation_exception_extra(
    extra: list[dict[str, Any]],
) -> str:
    result = []
    for item in extra:
        message = item["message"]
        key = item["key"]

        result.append(f"{key}：{message}")

    return "；".join(result)


def _not_found_exception_handler(_: Request, __: Exception) -> Response:
    return Response(b"", status_code=HTTP_404_NOT_FOUND)


def _validation_exception_handler(
    _: Request, exception: ValidationException
) -> Response:
    return error(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        message="数据校验失败",
        details=_generate_details_from_validation_exception_extra(exception.extra),  # type: ignore
    )


def _method_not_allowd_exception_handler(_: Request, __: Exception) -> Response:
    return Response(b"", status_code=HTTP_405_METHOD_NOT_ALLOWED)


def _internal_server_error_handler(_: Request, exception: Exception) -> Response:
    print(
        f"[{get_now_without_microsecond()}] 处理请求时发生异常：{exception.__repr__()}"
    )

    return error(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        message="未知服务端异常",
        details="请稍后再试或联系开发者",
    )


EXCEPTION_HANDLERS: ExceptionHandlersMap = {
    NotFoundException: _not_found_exception_handler,
    MethodNotAllowedException: _method_not_allowd_exception_handler,
    ValidationException: _validation_exception_handler,
    Exception: _internal_server_error_handler,
}
