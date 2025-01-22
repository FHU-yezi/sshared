from typing import Literal

from sshared.logging.types import LogLevelType
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
    display_level: LogLevelType
    save_level: LogLevelType

    @property
    def connection_string(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/logs"


class UvicornBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Port
    mode: Literal["DEBUG", "PROD"]
    workers: PositiveInt


class AliyunAccessKeyBlock(ConfigBlock, frozen=True):
    access_key_id: str
    access_key_secret: str


class FeishuAuthBlock(ConfigBlock, frozen=True):
    app_id: NonEmptyStr
    app_secret: NonEmptyStr


class FeishuBitableBlock(ConfigBlock, frozen=True):
    app_id: NonEmptyStr
    table_id: NonEmptyStr
