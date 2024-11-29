from __future__ import annotations

from typing import TYPE_CHECKING

from sshared.strict_struct import (
    NonEmptyStr,
    PositiveInt,
    StrictFrozenStruct,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class Index(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    keys: Sequence[NonEmptyStr]
    name: NonEmptyStr | None = None
    unique: bool = False
    expire_after_seconds: PositiveInt | None = None
