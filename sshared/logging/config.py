from sshared.logging.types import LogLevelEnum
from sshared.strict_struct import PositiveInt, StrictFrozenStruct
from sshared.terminal.color import Colors


class LogLevelConfigItem(StrictFrozenStruct, frozen=True, eq=False, gc=False):
    num: PositiveInt
    color: Colors


LOG_LEVEL_CONFIG: dict[LogLevelEnum, LogLevelConfigItem] = {
    LogLevelEnum.DEBUG: LogLevelConfigItem(num=1, color="BLUE"),
    LogLevelEnum.INFO: LogLevelConfigItem(num=2, color="GREEN"),
    LogLevelEnum.WARN: LogLevelConfigItem(num=3, color="YELLOW"),
    LogLevelEnum.ERROR: LogLevelConfigItem(num=4, color="RED"),
    LogLevelEnum.FATAL: LogLevelConfigItem(num=5, color="MAGENTA"),
}
