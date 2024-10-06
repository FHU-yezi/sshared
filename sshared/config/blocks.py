from typing import Annotated, Literal

from msgspec import Meta

from sshared.logging import _LogLevels
from sshared.strict_struct import NonEmptyStr, PositiveInt, StrictFrozenStruct


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


class MongoBlock(ConfigBlock, frozen=True):
    host: NonEmptyStr
    port: Annotated[int, Meta(gt=0, lt=65536)]
    database: NonEmptyStr


class LoggingBlock(ConfigBlock, frozen=True):
    enable_save: bool
    display_level: _LogLevels
    save_level: _LogLevels


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
