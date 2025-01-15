from __future__ import annotations

from msgspec import Struct

from sshared.strict_struct import StrictFrozenStruct


class RequestStruct(
    Struct,
    frozen=True,
    eq=False,
    forbid_unknown_fields=True,
    rename="camel",
    gc=False,
):
    pass


class ResponseStruct(
    StrictFrozenStruct,
    frozen=True,
    eq=False,
    rename="camel",
    gc=False,
):
    pass


class ErrorStruct(ResponseStruct, frozen=True):
    message: str
    details: str | None
