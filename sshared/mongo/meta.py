from typing import Optional, Sequence

from msgspec import Struct


class Index(Struct, frozen=True, eq=False, kw_only=True, gc=False):
    keys: Sequence[str]
    name: Optional[str] = None
    unique: bool = False
    expire_after_seconds: Optional[int] = None
