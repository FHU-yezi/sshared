from sshared.validatable_struct import ValidatableSturct


class View(ValidatableSturct, eq=False, forbid_unknown_fields=True):
    @classmethod
    async def _create_view(cls) -> None:
        pass

    @classmethod
    async def init(cls) -> None:
        await cls._create_view()
