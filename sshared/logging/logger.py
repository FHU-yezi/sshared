from __future__ import annotations

from datetime import datetime

from sshared.logging.config import LOG_LEVEL_CONFIG
from sshared.logging.record import ExceptionField, ExceptionStackField, Record
from sshared.logging.types import ExtraType, LogLevelType
from sshared.terminal.color import fg_color
from sshared.terminal.exception import get_exception_stack


class LoggerInitError(Exception):
    pass


class Logger:
    def __init__(
        self,
        display_level: LogLevelType = "DEBUG",
        save_level: LogLevelType = "DEBUG",
        connection_string: str | None = None,
        table: str | None = None,
    ) -> None:
        self._display_level_num = LOG_LEVEL_CONFIG[display_level].num
        self._save_level_num = LOG_LEVEL_CONFIG[save_level].num

        if connection_string and table:
            from psycopg import sql

            from sshared.postgres.connection_manager import SyncConnectionManager

            self._connection_manager = SyncConnectionManager(connection_string)
            self._insert_statement = sql.SQL(
                "INSERT INTO {} (time, level, msg, extra, exception) "
                "VALUES (%s, %s, %s, %s, %s);"
            ).format(sql.Identifier(table))
            self._init_db(table)
        else:
            self._connection_manager = None

    def _init_db(self, table: str) -> None:
        from psycopg import sql

        from sshared.postgres import enhance_json_process

        if self._connection_manager is None:
            raise LoggerInitError("未设置 Connection String，无法将日志保存到数据库")

        enhance_json_process()

        conn = self._connection_manager.get_conn()

        conn.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enum_logs_level') THEN
                    CREATE TYPE enum_logs_level AS ENUM ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL');
                END IF;
            END
            $$;
            """  # noqa: E501
        )

        conn.execute(
            sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id serial PRIMARY KEY,
                time TIMESTAMP NOT NULL,
                level enum_logs_level NOT NULL,
                msg TEXT NOT NULL,
                extra JSONB,
                exception JSONB
            )
            """).format(sql.Identifier(table))
        )

    def _print(self, record: Record) -> None:
        main_string: list[str] = [
            record.time.strftime(r"%y-%m-%d %H:%M:%S"),
            fg_color(f"{record.level:<5}", LOG_LEVEL_CONFIG[record.level].color),
            record.msg,
        ]

        if record.extra:
            main_string.extend(f"{key}={value}" for key, value in record.extra.items())

        print(" ".join(main_string))  # noqa: T201

        if record.exception:
            exception_string: list[str] = [
                fg_color("Exception", "RED"),
                f"{record.exception.name}({record.exception.desc})",
            ]

            if record.exception.stack:
                for x in record.exception.stack:
                    exception_string.extend(
                        [
                            "\n    ",
                            f"at {x.file_name}:{x.line_number} ->",
                            f"{x.func_name} -> {x.line}",
                        ]
                    )

            print(  # noqa: T201
                "                 ",  # 首行缩进
                " ".join(
                    # 对每一行进行缩进
                    x.replace("\n", "\n               ")
                    for x in exception_string
                ),
            )

    def _save(self, record: Record) -> None:
        from psycopg.types.json import Jsonb

        if self._connection_manager is None:
            raise LoggerInitError("未设置 Connection String，无法将日志保存到数据库")

        self._connection_manager.get_conn().execute(
            self._insert_statement,
            (
                record.time,
                record.level,
                record.msg,
                Jsonb(record.extra) if record.extra else None,
                Jsonb(record.exception) if record.exception else None,
            ),
            prepare=True,
        )

    def _log(
        self,
        msg: str,
        /,
        *,
        level: LogLevelType,
        exception: Exception | None,
        **kwargs: ExtraType,
    ) -> None:
        exc_stack = get_exception_stack(exception) if exception else None

        record = Record(
            time=datetime.now(),
            level=level,
            msg=msg,
            extra=kwargs if kwargs else None,
            exception=ExceptionField(
                name=type(exception).__name__,
                desc=repr(exception.args[0]) if len(exception.args) else None,
                stack=tuple(
                    ExceptionStackField(
                        file_name=item.file_name,
                        line_number=item.line_number,
                        func_name=item.func_name,
                        line=item.line,
                    )
                    for item in exc_stack
                )
                if exc_stack
                else None,
            )
            if exception
            else None,
        ).validate()

        if LOG_LEVEL_CONFIG[level].num >= self._display_level_num:
            self._print(record)

        if (
            LOG_LEVEL_CONFIG[level].num >= self._save_level_num
            and self._connection_manager is not None
        ):
            self._save(record)

    def debug(self, msg: str, /, **kwargs: ExtraType) -> None:
        self._log(msg, level="DEBUG", exception=None, **kwargs)

    def info(self, msg: str, /, **kwargs: ExtraType) -> None:
        self._log(msg, level="INFO", exception=None, **kwargs)

    def warn(
        self, msg: str, /, *, exception: Exception | None = None, **kwargs: ExtraType
    ) -> None:
        self._log(msg, level="WARN", exception=exception, **kwargs)

    def error(
        self, msg: str, /, *, exception: Exception | None = None, **kwargs: ExtraType
    ) -> None:
        self._log(msg, level="ERROR", exception=exception, **kwargs)

    def fatal(
        self, msg: str, /, *, exception: Exception | None = None, **kwargs: ExtraType
    ) -> None:
        self._log(msg, level="FATAL", exception=exception, **kwargs)
