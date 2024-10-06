from typing import Optional

from msgspec import Struct

from sshared.strict_struct import StrictStruct


class RequestStruct(
    Struct, eq=False, forbid_unknown_fields=True, rename="camel", gc=False
):
    pass


class ResponseStruct(StrictStruct, eq=False, rename="camel", gc=False):
    pass


class ErrorStruct(ResponseStruct):
    message: str
    details: Optional[str]
