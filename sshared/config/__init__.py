from typing import TypeVar

from msgspec.toml import decode

from sshared.strict_struct import StrictFrozenStruct

T = TypeVar("T")


class ConfigBase(
    StrictFrozenStruct,
    frozen=True,
    forbid_unknown_fields=True,
    eq=False,
    gc=False,
):
    @classmethod
    def load_from_file(cls: type[T], file_name: str, /) -> T:
        with open(file_name, "rb") as f:
            return decode(f.read(), type=cls)
