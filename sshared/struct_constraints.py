from typing import Annotated

from msgspec import Meta, Struct, convert, to_builtins
from typing_extensions import Self


class ValidatableSturct(Struct):
    def validate(self) -> Self:
        return convert(
            to_builtins(self),
            type=self.__class__,
        )


class ValidatableFrozenSturct(Struct, frozen=True):
    def validate(self) -> Self:
        return convert(
            to_builtins(self),
            type=self.__class__,
        )


PositiveInt = Annotated[int, Meta(gt=0)]
PositiveFloat = Annotated[float, Meta(gt=0)]
NonNegativeInt = Annotated[int, Meta(ge=0)]
NonNegativeFloat = Annotated[float, Meta(ge=0)]
NonEmptyStr = Annotated[str, Meta(min_length=1)]
Percentage = Annotated[float, Meta(ge=0, le=1)]
