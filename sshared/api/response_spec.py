from collections.abc import Sequence
from typing import Optional, Union

from litestar.openapi.datastructures import ResponseSpec

from .structs import ErrorStruct, ResponseStruct


def success_response_spec(
    response_obj: Optional[
        Union[type[ResponseStruct], type[Sequence[ResponseStruct]]]
    ] = None,
    description: str = "请求成功",
) -> ResponseSpec:
    return ResponseSpec(response_obj, generate_examples=False, description=description)


def error_response_spec(description: str) -> ResponseSpec:
    return ResponseSpec(ErrorStruct, generate_examples=False, description=description)
