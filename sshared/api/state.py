from litestar.datastructures import State

from sshared.logging import Logger
from sshared.postgres import Pool


def get_app_state(*, logger: Logger, db_pools: tuple[Pool, ...]) -> State:
    return State(
        {
            "logger": logger,
            "db_pools": db_pools,
        }
    )
