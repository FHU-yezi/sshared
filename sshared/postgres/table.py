from sshared.strict_struct import StrictFrozenStruct


class Table(StrictFrozenStruct, frozen=True, eq=False, forbid_unknown_fields=True):
    @classmethod
    async def _create_enum(cls) -> None:
        pass

    @classmethod
    async def _create_table(cls) -> None:
        pass

    @classmethod
    async def _create_index(cls) -> None:
        pass

    @classmethod
    async def init(cls) -> None:
        await cls._create_enum()
        await cls._create_table()
        await cls._create_index()

    async def create(self) -> None:
        pass
