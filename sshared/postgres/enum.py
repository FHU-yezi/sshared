from enum import Enum

from psycopg import sql
from psycopg.connection_async import AsyncConnection
from psycopg.types.enum import EnumInfo, register_enum


async def create_enum(
    *,
    conn: AsyncConnection,
    name: str,
    enum_class: type[Enum],
) -> None:
    await conn.execute(
        sql.SQL(
            """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = {}) THEN
                CREATE TYPE {} AS ENUM ({});
            END IF;
        END
        $$;
        """
        ).format(
            sql.Literal(name),
            sql.Identifier(name),
            sql.SQL(", ").join([sql.Literal(x.value) for x in enum_class]),
        )
    )
    enum_info = await EnumInfo.fetch(conn, name)
    register_enum(enum_info, conn, enum_class)  # type: ignore
