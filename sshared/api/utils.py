from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sshared.mongo.types import SortType


def parse_sort_string(string: str, /) -> "SortType":
    result: SortType = {}

    for item in string.split(","):
        if item.startswith("-"):
            result[item[1:]] = "DESC"
        else:
            result[item] = "ASC"

    return result
