from typing import Annotated, Literal

from msgspec import Meta

from sshared.logging import _LogLevels
from sshared.struct_constraints import NonEmptyStr, PositiveInt, ValidatableFrozenSturct

from ._meta import CONFIG_META


class MongoDBBlock(ValidatableFrozenSturct, frozen=True, **CONFIG_META):
    host: NonEmptyStr
    port: Annotated[int, Meta(gt=0, lt=65536)]
    database: NonEmptyStr


class LoggingBlock(ValidatableFrozenSturct, frozen=True, **CONFIG_META):
    enable_save: bool
    display_level: _LogLevels
    save_level: _LogLevels


class UvicornBlock(ValidatableFrozenSturct, frozen=True, **CONFIG_META):
    host: NonEmptyStr
    port: Annotated[int, Meta(gt=0, lt=65536)]
    log_level: Literal["critical", "error", "warning", "info", "debug", "trace"]
    workers: PositiveInt
    reload: bool
    access_log: bool


class FeishuAuthBlock(ValidatableFrozenSturct, frozen=True, **CONFIG_META):
    app_id: NonEmptyStr
    app_secret: NonEmptyStr


class FeishuBitableBlock(ValidatableFrozenSturct, frozen=True, **CONFIG_META):
    app_id: NonEmptyStr
    table_id: NonEmptyStr
