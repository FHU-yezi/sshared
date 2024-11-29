from sshared.strict_struct import StrictFrozenStruct


class View(StrictFrozenStruct, frozen=True, eq=False, forbid_unknown_fields=True):
    pass
