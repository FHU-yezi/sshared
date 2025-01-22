from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Callable

from litestar import Litestar

from sshared.logging import Logger
from sshared.postgres import Pool


@asynccontextmanager
async def db_pools_lifespan(app: Litestar) -> AsyncGenerator[None]:
    db_pools: tuple[Pool, ...] = app.state.db_pools
    logger: Logger = app.state.logger

    for pool in db_pools:
        await pool.prepare()
        logger.debug("数据库连接池已开启")

    try:
        yield
    finally:
        for pool in db_pools:
            await pool.close()
            logger.debug("数据库连接池已关闭")


LIFESPANS: tuple[Callable[[Litestar], AbstractAsyncContextManager], ...] = (
    db_pools_lifespan,
)
