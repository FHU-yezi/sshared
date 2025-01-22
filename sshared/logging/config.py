from sshared.logging.types import LogLevelType
from sshared.strict_struct import PositiveInt, StrictFrozenStruct
from sshared.terminal.color import Colors


class LogLevelConfigItem(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    num: PositiveInt
    color: Colors


LOG_LEVEL_CONFIG: dict[LogLevelType, LogLevelConfigItem] = {
    "DEBUG": LogLevelConfigItem(num=1, color="BLUE"),
    "INFO": LogLevelConfigItem(num=2, color="GREEN"),
    "WARN": LogLevelConfigItem(num=3, color="YELLOW"),
    "ERROR": LogLevelConfigItem(num=4, color="RED"),
    "FATAL": LogLevelConfigItem(num=5, color="MAGENTA"),
}
