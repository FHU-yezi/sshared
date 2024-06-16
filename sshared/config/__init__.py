from msgspec.toml import decode
from typing_extensions import Self

from sshared.struct_constraints import ValidatableFrozenSturct

from ._meta import CONFIG_META


class ConfigBase(ValidatableFrozenSturct, frozen=True, **CONFIG_META):
    @classmethod
    def load_from_file(cls, file_name: str, /) -> Self:
        with open(file_name, "rb") as f:
            return decode(f.read(), type=cls)
