from typing import Optional, Sequence

from sshared.struct_constraints import (
    NonEmptyStr,
    PositiveInt,
    ValidatableFrozenSturct,
)


class Index(ValidatableFrozenSturct, frozen=True, eq=False, gc=False):
    keys: Sequence[NonEmptyStr]
    name: Optional[NonEmptyStr] = None
    unique: bool = False
    expire_after_seconds: Optional[PositiveInt] = None
