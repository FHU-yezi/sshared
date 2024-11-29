from __future__ import annotations

from time import sleep as sync_sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from psycopg import Connection


class SyncConnectionManager:
    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string
        self._conn: Connection | None = None
        self._connecting = False

    def _blocking_connect(self) -> None:
        from psycopg import Connection, OperationalError

        self._connecting = True

        while True:
            try:
                self._conn = Connection.connect(
                    self._connection_string, autocommit=True
                )
                self._connecting = False
            except OperationalError:
                sync_sleep(0.1)
            else:
                return

    def _blocking_waiting_for_conn(self) -> Connection:
        while True:
            if self._conn:
                return self._conn

            sync_sleep(0.03)

    def _check(self) -> bool:
        from psycopg import OperationalError

        if not self._conn:
            return False

        try:
            self._conn.execute("")
        except OperationalError:
            return False
        else:
            return True

    def get_conn(self) -> Connection:
        # 尚未连接
        if not self._conn:
            # 如果正在尝试连接，阻塞等待
            if self._connecting:
                return self._blocking_waiting_for_conn()

            # 否则，尝试连接并返回
            self._blocking_connect()
            return self._conn  # type: ignore

        # 已连接，检查状态
        ok = self._check()
        # 如果状态异常，重新连接
        if not ok:
            # 如果正在尝试连接，阻塞等待
            if self._connecting:
                return self._blocking_waiting_for_conn()

            # 否则，尝试连接
            self._blocking_connect()

        # 状态正常，返回
        return self._conn  # type: ignore
