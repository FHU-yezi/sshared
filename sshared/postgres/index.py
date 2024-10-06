from typing import Literal

from psycopg import sql
from psycopg.connection_async import AsyncConnection

IndexMethod = Literal["B-Tree", "Hash", "GiST", "SP-GiST", "GIN", "BRIN"]
_METHOD_MEPPING: dict[IndexMethod, str] = {
    "B-Tree": "btree",
    "Hash": "hash",
    "GiST": "gist",
    "SP-GiST": "spgist",
    "GIN": "gin",
    "BRIN": "brin",
}


async def create_index(
    *,
    conn: AsyncConnection,
    name: str,
    table: str,
    fields: tuple[str, ...],
    method: IndexMethod = "B-Tree",
    unique: bool = False,
) -> None:
    if not unique:
        await conn.execute(
            sql.SQL(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS {name} "
                "ON {table} USING {method} ({fields});"
            ).format(
                name=sql.Identifier(name),
                table=sql.Identifier(table),
                method=sql.Identifier(_METHOD_MEPPING[method]),
                fields=sql.SQL(", ").join([sql.Identifier(x) for x in fields]),
            )
        )
    else:
        await conn.execute(
            sql.SQL(
                "CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS {name} "
                "ON {table} USING {method} ({fields});"
            ).format(
                name=sql.Identifier(name),
                table=sql.Identifier(table),
                method=sql.Identifier(_METHOD_MEPPING[method]),
                fields=sql.SQL(", ").join([sql.Identifier(x) for x in fields]),
            )
        )
