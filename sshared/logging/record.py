from __future__ import annotations

from typing import TYPE_CHECKING

from sshared.strict_struct import NonEmptyStr, PositiveInt, StrictFrozenStruct

if TYPE_CHECKING:
    from datetime import datetime

    from sshared.logging.types import ExtraType, LogLevelEnum


class ExceptionStackField(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    file_name: str
    line_number: PositiveInt | None
    func_name: NonEmptyStr
    line: NonEmptyStr | None


class ExceptionField(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    name: NonEmptyStr
    desc: NonEmptyStr | None
    stack: tuple[ExceptionStackField, ...] | None


class Record(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    time: datetime
    level: LogLevelEnum
    msg: NonEmptyStr
    extra: dict[NonEmptyStr, ExtraType] | None
    exception: ExceptionField | None
