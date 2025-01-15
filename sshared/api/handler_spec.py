from __future__ import annotations

from collections.abc import Sequence

from litestar.openapi.datastructures import ResponseSpec
from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .structs import ErrorStruct, ResponseStruct


def get_handler_spec_params(  # noqa: PLR0913
    *,
    name: str,
    success_status_code: int,
    success_response: type[ResponseStruct] | type[Sequence[ResponseStruct]] | None,
    error_responses: dict[int, str] | None = None,
    tag: str | None = None,
    deprecated: bool = False,
) -> dict:
    if not error_responses:
        error_responses = {}

    return {
        "summary": name,
        "tags": (tag,) if tag else (),
        "deprecated": deprecated,
        "responses": {
            success_status_code: ResponseSpec(
                data_container=success_response,
                description="成功",
                generate_examples=False,
            ),
            HTTP_400_BAD_REQUEST: ResponseSpec(
                data_container=ErrorStruct,
                description="数据格式异常",
                generate_examples=False,
            ),
            HTTP_422_UNPROCESSABLE_ENTITY: ResponseSpec(
                data_container=ErrorStruct,
                description="数据校验失败",
                generate_examples=False,
            ),
            HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
                data_container=ErrorStruct,
                description="未知异常",
                generate_examples=False,
            ),
            **{
                status_code: ResponseSpec(
                    data_container=ErrorStruct,
                    description=description,
                    generate_examples=False,
                )
                for status_code, description in error_responses.items()
            },
        },
    }
