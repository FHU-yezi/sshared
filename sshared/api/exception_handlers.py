from __future__ import annotations

from re import compile as re_compile

from litestar import Request
from litestar.exceptions import (
    MethodNotAllowedException,
    NotFoundException,
    ValidationException,
)
from litestar.response import Response
from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.types import ExceptionHandlersMap

from sshared.logging import Logger

from .response import error

BAD_REQUEST_TARGETS: tuple[str, ...] = ("JSON is malformed", "Input data was truncated")

MISSING_FIELD_REGEX = re_compile(r"Object missing required field `(.*)`")
WRONG_FIELD_TYPE_REGEX = re_compile(r"Expected `(.*)`, got `(.*)`")
STRING_FIELD_PATTERN_CONSTRAINT_REGEX = re_compile(
    r"Expected `str` matching regex '(.*)'"
)
STRING_FIELD_CONSTRAINT_REGEX = re_compile(r"Expected `str` of (.*)")
NUMBER_FIELD_MULTIPLE_OF_CONSTRAINT_REGEX = re_compile(
    r"Expected `(int|float)` that's a multiple of (.*)"
)
NUMBER_FIELD_CONSTRAINT_REGEX = re_compile(r"Expected `(int|float)` .*")


def get_validation_exception_details(
    exception_data: list[dict[str, str]],
) -> str:
    result: list[str] = []

    for item in exception_data:
        if match := MISSING_FIELD_REGEX.match(item["message"]):
            field_name = match.group()
            result.append(f"字段 {field_name} 缺失")
        elif match := WRONG_FIELD_TYPE_REGEX.match(item["message"]):
            expected_type, actural_type = match.groups()
            result.append(
                f"字段 {item['key']} 的类型应为 {expected_type}，而不是 {actural_type}"
            )
        elif match := STRING_FIELD_PATTERN_CONSTRAINT_REGEX.match(item["message"]):
            pattern = match.group(1)
            result.append(f"字段 {item['key']} 必须匹配正则表达式 /{pattern}/")
        elif match := STRING_FIELD_CONSTRAINT_REGEX.match(item["message"]):
            pattern = match.group(1)
            result.append(f"字段 {item['key']} 必须满足约束 {pattern}")
        elif match := NUMBER_FIELD_MULTIPLE_OF_CONSTRAINT_REGEX.match(item["message"]):
            multiple_of = match.group(2)
            result.append(f"字段 {item['key']} 必须是 {multiple_of} 的倍数")
        elif match := NUMBER_FIELD_CONSTRAINT_REGEX.match(item["message"]):
            pattern = match.group(2)
            result.append(f"字段 {item['key']} 必须满足约束 {pattern}")
        else:
            result.append(item["message"])

    return "；".join(result)


def not_found_exception_handler(_: Request, __: NotFoundException) -> Response:
    return Response(b"", status_code=HTTP_404_NOT_FOUND)


def method_not_allowed_exception_handler(
    _: Request, __: MethodNotAllowedException
) -> Response:
    return Response(b"", status_code=HTTP_405_METHOD_NOT_ALLOWED)


def validation_exception_handler(
    request: Request, exception: ValidationException
) -> Response:
    # 如果可行，提取详细错误信息并写入 details 字段
    if isinstance(exception.extra, list):
        details = get_validation_exception_details(exception.extra)
    else:
        logger: Logger = request.app.state.logger
        logger.warn("无法获取数据校验失败异常详情")

        details = None

    return error(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        message="数据校验失败",
        details=details,
    )


def unknown_exception_handler(request: Request, exception: Exception) -> Response:
    if exception.args and any(x in exception.args[0] for x in BAD_REQUEST_TARGETS):
        return error(
            status_code=HTTP_400_BAD_REQUEST,
            message="数据格式异常",
            details="请检查请求体格式",
        )

    logger: Logger = request.app.state.logger
    logger.error("处理请求时发生异常", exception=exception)

    return error(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        message="未知异常",
        details="请重试或联系开发者",
    )


EXCEPTION_HANDLERS: ExceptionHandlersMap = {
    NotFoundException: not_found_exception_handler,
    MethodNotAllowedException: method_not_allowed_exception_handler,
    ValidationException: validation_exception_handler,
    Exception: unknown_exception_handler,
}
