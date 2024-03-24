from typing import Optional, Sequence

from msgspec import Struct

_META_CONFIG = {
    "frozen": True,
    "eq": False,
    "kw_only": True,
    "gc": False,
}


class Index(Struct, **_META_CONFIG):
    keys: Sequence[str]
    name: Optional[str] = None
    unique: bool = False
    expire_after_seconds: Optional[int] = None
