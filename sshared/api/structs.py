from typing import Optional

from msgspec import Struct

from sshared.strict_struct import StrictSturct


class RequestStruct(
    Struct, eq=False, forbid_unknown_fields=True, rename="camel", gc=False
):
    pass


class ResponseStruct(StrictSturct, eq=False, rename="camel", gc=False):
    pass


class ErrorStruct(ResponseStruct):
    message: str
    details: Optional[str]
