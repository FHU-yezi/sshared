from asyncio import Queue, QueueEmpty, sleep
from contextlib import asynccontextmanager, suppress
from random import random
from typing import Optional

from psycopg import AsyncConnection, OperationalError


class Pool:
    def __init__(
        self,
        connection_string: str,
        *,
        min_size: int,
        max_size: int,
        app_name: Optional[str] = None,
    ) -> None:
        self._connection_string = connection_string
        self._min_size = min_size
        self._max_size = max_size
        self._app_name = app_name

        self._total_conns_count: int = 0
        self._avaliable_conns: Queue[AsyncConnection] = Queue()

    async def _new_conn(self) -> AsyncConnection:
        """创建新连接。

        如果遇到异常，以随机间隔（最多不超过 0.25s）重试，直到连接成功。
        """
        while True:
            try:
                conn = await AsyncConnection.connect(
                    self._connection_string,
                    autocommit=True,
                    application_name=self._app_name,
                    sslmode="disable",
                )
            except OperationalError:  # noqa: PERF203
                await sleep(random() / 4)  # noqa: S311
            else:
                self._total_conns_count += 1
                return conn

    async def close_conn(self, conn: AsyncConnection) -> None:
        """关闭连接。

        如果该连接已关闭，不作任何事。
        如果关闭连接时发生异常，视为关闭成功并正常返回。
        """
        if conn.closed:
            return

        with suppress(OperationalError):
            await conn.close()
        self._total_conns_count -= 1

    async def _check_conn(self, conn: AsyncConnection) -> bool:
        """检测连接是否正常。"""
        try:
            await conn.execute("")
        except OperationalError:
            return False
        else:
            return True

    async def _block_get_conn_from_pool(self) -> AsyncConnection:
        """从连接池中获取连接。

        如果没有可用的连接，阻塞等待。
        """
        return await self._avaliable_conns.get()

    async def prepare(self) -> None:
        """创建新连接，直到连接池至少有 min_size 个连接。"""
        while self._avaliable_conns.qsize() < self._min_size:
            self._avaliable_conns.put_nowait(await self._new_conn())

    async def close(self) -> None:
        """关闭连接池中的所有连接。

        调用此方法后，该连接池不应再被使用。
        """
        while not self._avaliable_conns.empty():
            conn = self._avaliable_conns.get_nowait()
            await self.close_conn(conn)

    @asynccontextmanager
    async def get_conn(self):  # noqa: ANN201
        """获取连接。

        如果没有可用的连接，该函数将阻塞，直到有连接可用。
        """
        while True:
            try:
                # 先尝试直接从连接池中获取连接
                conn = self._avaliable_conns.get_nowait()
            except QueueEmpty:
                # 连接池中没有可用的连接
                # 如果连接数量未达到上限，创建新连接
                if self._total_conns_count < self._max_size:
                    conn = await self._new_conn()
                # 如果连接数量达到上限，阻塞并等待有连接可用
                else:
                    conn = await self._block_get_conn_from_pool()

            # 检查连接是否正常，如果正常则跳出循环，将连接交给调用方
            if await self._check_conn(conn):
                break

            # 如果连接不正常，该连接将不会被归还到可用连接池中
            # 此时减少总连接数量，之后继续循环执行获取连接逻辑
            self._total_conns_count -= 1

        try:
            yield conn
        finally:
            # 将连接归还到可用连接池中
            self._avaliable_conns.put_nowait(conn)
