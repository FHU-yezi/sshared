from typing import Annotated, Literal

from msgspec import Meta

from sshared.logging.types import LogLevelEnum
from sshared.strict_struct import NonEmptyStr, PositiveInt, StrictFrozenStruct


class ConfigBlock(
    StrictFrozenStruct,
    frozen=True,
    forbid_unknown_fields=True,
    eq=False,
    gc=False,
):
    pass


class MongoBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Annotated[int, Meta(gt=0, lt=65536)]
    database: NonEmptyStr


class PostgresBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Annotated[int, Meta(gt=0, lt=65536)]
    user: NonEmptyStr
    password: NonEmptyStr
    database: NonEmptyStr

    @property
    def connection_string(self) -> str:
        return (
            f"postgres://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class LoggingBlock(ConfigBlock, frozen=True):
    display_level: LogLevelEnum
    save_level: LogLevelEnum


class GotifyBlock(ConfigBlock, frozen=True):
    enabled: bool
    host: str
    port: Annotated[int, Meta(gt=0, lt=65536)]
    token: str


class UvicornBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Annotated[int, Meta(gt=0, lt=65536)]
    log_level: Literal["critical", "error", "warning", "info", "debug", "trace"]
    workers: PositiveInt
    reload: bool
    access_log: bool


class FeishuAuthBlock(ConfigBlock, frozen=True):
    app_id: NonEmptyStr
    app_secret: NonEmptyStr


class FeishuBitableBlock(ConfigBlock, frozen=True):
    app_id: NonEmptyStr
    table_id: NonEmptyStr
