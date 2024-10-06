from typing import Literal

Colors = Literal["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]

_RESET = "\033[0m"
_FOREGROUND_COLORS: dict[Colors, int] = {
    "BLACK": 30,
    "RED": 31,
    "GREEN": 32,
    "YELLOW": 33,
    "BLUE": 34,
    "MAGENTA": 35,
    "CYAN": 36,
    "WHITE": 37,
}
_BACKGROUND_COLORS: dict[Colors, int] = {
    "BLACK": 40,
    "RED": 41,
    "GREEN": 42,
    "YELLOW": 43,
    "BLUE": 44,
    "MAGENTA": 45,
    "CYAN": 46,
    "WHITE": 47,
}


def fg_color(
    string: str,
    /,
    color: Colors,
    *,
    reset: bool = True,
) -> str:
    result = f"\033[{_FOREGROUND_COLORS[color]}m{string}"

    if not reset:
        return result

    return result + _RESET


def bg_color(
    string: str,
    /,
    color: Colors,
    *,
    reset: bool = True,
) -> str:
    # 对于红色和紫色，使用白色字体提高对比度
    # 对于其它颜色，使用黑色
    fg_color = 37 if color in {"RED", "MAGENTA"} else 30
    result = f"\033[0;{fg_color};{_BACKGROUND_COLORS[color]}m{string}"

    if not reset:
        return result

    return result + _RESET
