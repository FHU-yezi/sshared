from asyncio import run as asyncio_run
from collections import deque
from datetime import datetime
from threading import Lock, Thread
from time import sleep
from typing import Dict, Literal, Optional, Union

from motor.motor_asyncio import AsyncIOMotorCollection
from msgspec import Struct, to_builtins

from sshared.terminal.color import Colors, fg_color
from sshared.terminal.exception import pretty_exception

_LogLevels = Literal["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
_ExtraType = Union[
    int,
    float,
    str,
    None,
]


class _LogLevelConfigItem(Struct, frozen=True, eq=False, gc=False):
    num: int
    color: Colors


_LogLevelConfig: Dict[_LogLevels, _LogLevelConfigItem] = {
    "DEBUG": _LogLevelConfigItem(num=1, color="BLUE"),
    "INFO": _LogLevelConfigItem(num=2, color="GREEN"),
    "WARN": _LogLevelConfigItem(num=3, color="YELLOW"),
    "ERROR": _LogLevelConfigItem(num=4, color="RED"),
    "FATAL": _LogLevelConfigItem(num=5, color="MAGENTA"),
}


class _ExceptionField(
    Struct, rename="camel", frozen=True, eq=False, kw_only=True, gc=False
):
    name: str
    desc: Optional[str]


class _Record(Struct, rename="camel", frozen=True, eq=False, kw_only=True, gc=False):
    time: datetime
    level: _LogLevels
    msg: str
    extra: Optional[Dict[str, _ExtraType]]
    exc: Optional[_ExceptionField]


class Logger:
    def __init__(
        self,
        display_level: _LogLevels = "DEBUG",
        store_level: _LogLevels = "INFO",
        store_collection: Optional[AsyncIOMotorCollection] = None,
        store_interval: int = 3,
    ) -> None:
        self._display_level: _LogLevels = display_level
        self._store_level: _LogLevels = store_level

        self._store_collection = store_collection
        self._pending_queue: deque[_Record] = deque()
        self._pending_queue_lock = Lock()
        self._store_interval = store_interval

        if self._store_collection is not None:
            Thread(
                target=self.background_save_thread,
                name="logger-background-save",
                daemon=True,
            ).start()

    def _print(self, record: _Record) -> None:
        print(
            record.time.strftime(r"%y-%m-%d %H:%M:%S"),
            fg_color(f"{record.level:<5}", _LogLevelConfig[record.level].color),
            record.msg,
        )

        if record.extra:
            print(
                " ",  # 缩进两格，print sep 会自动加入一个空格
                fg_color("Extra", "BLUE"),
                " ".join(f"{key}={value}" for key, value in record.extra.items()),
            )

    def _add_to_pending_queue(self, record: _Record) -> None:
        with self._pending_queue_lock:
            self._pending_queue.append(record)

    async def _save_pending(self) -> None:
        if self._store_collection is None:
            raise ValueError("未指定用于存储日志信息的 MongoDB 集合")

        with self._pending_queue_lock:
            data = tuple(self._pending_queue)
            self._pending_queue.clear()

        if not data:
            return

        await self._store_collection.insert_many(to_builtins(item) for item in data)

    def background_save_thread(self) -> None:
        while True:
            sleep(self._store_interval)
            asyncio_run(self._save_pending())

    def _log(
        self,
        /,
        msg: str,
        *,
        level: _LogLevels,
        exc: Optional[Exception],
        **kwargs: _ExtraType,
    ) -> None:
        record = _Record(
            time=datetime.now(),
            level=level,
            msg=msg,
            extra=kwargs,
            exc=_ExceptionField(
                name=type(exc).__name__,
                desc=repr(exc.args[0]) if len(exc.args) else None,
            )
            if exc
            else None,
        )

        if _LogLevelConfig[level].num >= _LogLevelConfig[self._display_level].num:
            self._print(record)

        if (
            _LogLevelConfig[level].num >= _LogLevelConfig[self._store_level].num
            and self._store_collection is not None
        ):
            self._add_to_pending_queue(record)

    def debug(self, /, msg: str, **kwargs: _ExtraType) -> None:
        self._log(msg, level="DEBUG", exc=None, **kwargs)

    def info(self, /, msg: str, **kwargs: _ExtraType) -> None:
        self._log(msg, level="INFO", exc=None, **kwargs)

    def warn(
        self, /, msg: str, exc: Optional[Exception] = None, **kwargs: _ExtraType
    ) -> None:
        self._log(msg, level="WARN", exc=exc, **kwargs)
        # TODO
        if exc:
            print("  " + pretty_exception(exc).replace("\n", "\n  "))

    def error(
        self, /, msg: str, exc: Optional[Exception] = None, **kwargs: _ExtraType
    ) -> None:
        self._log(msg, level="ERROR", exc=exc, **kwargs)
        # TODO
        if exc:
            print("  " + pretty_exception(exc).replace("\n", "\n  "))

    def fatal(
        self, /, msg: str, exc: Optional[Exception] = None, **kwargs: _ExtraType
    ) -> None:
        self._log(msg, level="FATAL", exc=exc, **kwargs)
        # TODO
        if exc:
            print("  " + pretty_exception(exc).replace("\n", "\n  "))
