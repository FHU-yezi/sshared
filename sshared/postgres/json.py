from msgspec.json import decode, encode
from psycopg.types.json import set_json_dumps, set_json_loads


def enhance_json_process() -> None:
    set_json_dumps(encode)
    set_json_loads(decode)
