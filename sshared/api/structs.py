from msgspec import Struct

from sshared.struct_constraints import ValidatableSturct


class RequestStruct(
    Struct, eq=False, forbid_unknown_fields=True, rename="camel", gc=False
):
    pass


class ResponseStruct(ValidatableSturct, eq=False, rename="camel", gc=False):
    pass


class ErrorStruct(ResponseStruct):
    message: str
    details: str
