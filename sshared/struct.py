from msgspec import Struct, convert, to_builtins
from typing_extensions import Self


class ValidatableSturct(Struct):
    def validate(self) -> Self:
        return convert(
            to_builtins(self),
            type=self.__class__,
        )
