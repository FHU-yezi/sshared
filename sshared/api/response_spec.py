from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.openapi.datastructures import ResponseSpec

from .structs import ErrorStruct, ResponseStruct

if TYPE_CHECKING:
    from collections.abc import Sequence


def success_response_spec(
    response_obj: type[ResponseStruct] | type[Sequence[ResponseStruct]] | None = None,
    description: str = "请求成功",
) -> ResponseSpec:
    return ResponseSpec(response_obj, generate_examples=False, description=description)


def error_response_spec(description: str) -> ResponseSpec:
    return ResponseSpec(ErrorStruct, generate_examples=False, description=description)
