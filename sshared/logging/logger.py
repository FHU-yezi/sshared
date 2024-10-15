from datetime import datetime
from typing import Optional

from psycopg import sql

from sshared.logging.config import LOG_LEVEL_CONFIG
from sshared.logging.record import ExceptionField, ExceptionStackField, Record
from sshared.logging.types import ExtraType, LogLevelEnum
from sshared.terminal.color import fg_color
from sshared.terminal.exception import get_exception_stack


class Logger:
    def __init__(
        self,
        display_level: LogLevelEnum = LogLevelEnum.DEBUG,
        save_level: LogLevelEnum = LogLevelEnum.DEBUG,
        connection_string: Optional[str] = None,
        table: Optional[str] = None,
    ) -> None:
        self._display_level_num = LOG_LEVEL_CONFIG[display_level].num
        self._save_level_num = LOG_LEVEL_CONFIG[save_level].num

        if connection_string and table:
            from psycopg import Connection

            self._conn = Connection.connect(connection_string, autocommit=True)
            self._insert_statement = sql.SQL(
                "INSERT INTO {} (time, level, msg, extra, exception) "
                "VALUES (%s, %s, %s, %s, %s);"
            ).format(sql.Identifier(table))
            self._init_db(table)
        else:
            self._conn = None

    def _init_db(self, table: str) -> None:
        from psycopg.types.enum import EnumInfo, register_enum

        from sshared.postgres import enhance_json_process

        if self._conn is None:
            raise Exception("未设置 Connection String，无法将日志保存到数据库")

        enhance_json_process()

        self._conn.execute(
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
        enum_info = EnumInfo.fetch(self._conn, "enum_logs_level")
        register_enum(enum_info, self._conn, LogLevelEnum)  # type: ignore

        self._conn.execute(
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
        print(
            record.time.strftime(r"%y-%m-%d %H:%M:%S"),
            fg_color(f"{record.level.value:<5}", LOG_LEVEL_CONFIG[record.level].color),
            record.msg,
        )

        if record.extra:
            print(
                "                       ",  # 与 msg 对齐
                fg_color("Extra", "BLUE"),
                " ".join(f"{key}={value}" for key, value in record.extra.items()),
            )

        if record.exception:
            print(
                "                       ",  # 与 msg 对齐
                fg_color("Exception", "RED"),
                f"{record.exception.name}({record.exception.desc})",
            )

            if record.exception.stack:
                for x in record.exception.stack:
                    print(
                        "                                 ",  # 与 Exception 主体对齐
                        f"at {x.file_name}:{x.line_number} ->",
                        f"{x.func_name} -> {x.line}",
                    )

    def _save(self, record: Record) -> None:
        from psycopg.types.json import Jsonb

        if self._conn is None:
            raise Exception("未设置 Connection String，无法将日志保存到数据库")

        self._conn.execute(
            self._insert_statement,
            (
                record.time,
                record.level,
                record.msg,
                Jsonb(record.extra) if record.extra else None,
                Jsonb(record.exception) if record.exception else None,
            ),
        )

    def _log(
        self,
        /,
        msg: str,
        *,
        level: LogLevelEnum,
        exception: Optional[Exception],
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
            and self._conn is not None
        ):
            self._save(record)

    def debug(self, /, msg: str, **kwargs: ExtraType) -> None:
        self._log(msg, level=LogLevelEnum.DEBUG, exception=None, **kwargs)

    def info(self, /, msg: str, **kwargs: ExtraType) -> None:
        self._log(msg, level=LogLevelEnum.INFO, exception=None, **kwargs)

    def warn(
        self, /, msg: str, exception: Optional[Exception] = None, **kwargs: ExtraType
    ) -> None:
        self._log(msg, level=LogLevelEnum.WARN, exception=exception, **kwargs)

    def error(
        self, /, msg: str, exception: Optional[Exception] = None, **kwargs: ExtraType
    ) -> None:
        self._log(msg, level=LogLevelEnum.ERROR, exception=exception, **kwargs)

    def fatal(
        self, /, msg: str, exception: Optional[Exception] = None, **kwargs: ExtraType
    ) -> None:
        self._log(msg, level=LogLevelEnum.FATAL, exception=exception, **kwargs)
