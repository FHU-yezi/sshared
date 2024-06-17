from msgspec.toml import decode
from typing_extensions import Self

from sshared.validatable_struct import ValidatableFrozenSturct


class ConfigBase(
    ValidatableFrozenSturct,
    frozen=True,
    forbid_unknown_fields=True,
    eq=False,
    gc=False,
):
    @classmethod
    def load_from_file(cls, file_name: str, /) -> Self:
        with open(file_name, "rb") as f:
            return decode(f.read(), type=cls)
