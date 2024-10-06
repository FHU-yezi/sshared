from sshared.strict_struct import StrictStruct


class MaterializedView(StrictStruct, eq=False, forbid_unknown_fields=True):
    @classmethod
    async def _create_materialized_view(cls) -> None:
        pass

    @classmethod
    async def _create_index(cls) -> None:
        pass

    @classmethod
    async def init(cls) -> None:
        await cls._create_materialized_view()
        await cls._create_index()

    @classmethod
    async def refresh(cls) -> None:
        pass
