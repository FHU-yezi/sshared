from typing import Literal

from sshared.logging.types import LogLevelEnum
from sshared.strict_struct import NonEmptyStr, Port, PositiveInt, StrictFrozenStruct


class ConfigBlock(
    StrictFrozenStruct,
    frozen=True,
    forbid_unknown_fields=True,
    eq=False,
    gc=False,
):
    pass


class PostgresBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Port
    user: NonEmptyStr
    password: NonEmptyStr
    database: NonEmptyStr

    @property
    def connection_string(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class LoggingBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Port
    user: NonEmptyStr
    password: NonEmptyStr
    table: str
    display_level: LogLevelEnum
    save_level: LogLevelEnum

    @property
    def connection_string(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/logs"


class GotifyBlock(ConfigBlock, frozen=True):
    enabled: bool
    host: str
    port: Port
    token: str


class UvicornBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Port
    log_level: Literal["critical", "error", "warning", "info", "debug", "trace"]
    workers: PositiveInt
    reload: bool
    access_log: bool


class AliyunAccessKeyBlock(ConfigBlock, frozen=True):
    access_key_id: str
    access_key_secret: str


class FeishuAuthBlock(ConfigBlock, frozen=True):
    app_id: NonEmptyStr
    app_secret: NonEmptyStr


class FeishuBitableBlock(ConfigBlock, frozen=True):
    app_id: NonEmptyStr
    table_id: NonEmptyStr
