from sshared.strict_struct import StrictFrozenStruct


class MaterializedView(
    StrictFrozenStruct, frozen=True, eq=False, forbid_unknown_fields=True
):
    pass
