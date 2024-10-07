from datetime import datetime
from typing import Optional

from sshared.logging.types import ExtraType, LogLevelEnum
from sshared.strict_struct import NonEmptyStr, PositiveInt, StrictFrozenStruct


class ExceptionStackField(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    file_name: str
    line_number: Optional[PositiveInt]
    func_name: NonEmptyStr
    line: Optional[NonEmptyStr]


class ExceptionField(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    name: NonEmptyStr
    desc: Optional[NonEmptyStr]
    stack: Optional[tuple[ExceptionStackField, ...]]


class Record(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    time: datetime
    level: LogLevelEnum
    msg: NonEmptyStr
    extra: Optional[dict[NonEmptyStr, ExtraType]]
    exception: Optional[ExceptionField]
