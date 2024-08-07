from typing import Optional

from msgspec import Struct

from sshared.validatable_struct import ValidatableSturct


class RequestStruct(
    Struct, eq=False, forbid_unknown_fields=True, rename="camel", gc=False
):
    pass


class ResponseStruct(ValidatableSturct, eq=False, rename="camel", gc=False):
    pass


class ErrorStruct(ResponseStruct):
    message: str
    details: Optional[str]
