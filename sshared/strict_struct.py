from typing import Annotated, TypeVar

from msgspec import Meta, Struct, convert, to_builtins

T = TypeVar("T", bound="StrictStruct")
P = TypeVar("P", bound="StrictFrozenStruct")


class StrictStruct(Struct):
    def validate(self: T) -> T:
        return convert(
            to_builtins(self),
            type=self.__class__,
        )


class StrictFrozenStruct(Struct, frozen=True):
    def validate(self: P) -> P:
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
