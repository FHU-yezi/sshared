from sshared.strict_struct import StrictFrozenStruct


class Table(StrictFrozenStruct, frozen=True, eq=False, forbid_unknown_fields=True):
    pass
