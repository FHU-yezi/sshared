from msgspec import Struct


class RequestStruct(
    Struct, eq=False, forbid_unknown_fields=True, rename="camel", gc=False
):
    pass


class ResponseStruct(Struct, eq=False, rename="camel", gc=False):
    pass


class ErrorStruct(ResponseStruct):
    message: str
    details: str
