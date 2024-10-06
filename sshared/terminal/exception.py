from traceback import extract_tb
from typing import Optional

from sshared.strict_struct import StrictFrozenStruct

from .color import fg_color


class _ExceptionStack(StrictFrozenStruct, frozen=True, eq=False):
    file_name: str
    line_number: Optional[int]
    func_name: str
    line: Optional[str]


def get_exception_stack(exc: Exception, /) -> tuple[_ExceptionStack, ...]:
    stack = extract_tb(exc.__traceback__)
    return tuple(
        _ExceptionStack(
            file_name=item.filename.split("/")[-1],
            line_number=item.lineno,
            func_name=item.name,
            line=item.line,
        ).validate()
        for item in stack
    )


def pretty_exception(exc: Exception, /) -> str:
    exc_summary = (
        f"{type(exc).__name__}({exc.args[0]!r})"
        if exc.args
        else f"{type(exc).__name__}"
    )
    result: list[str] = [f"{fg_color('Exception', 'RED')} {exc_summary}"]

    for item in get_exception_stack(exc):
        file_name_and_line_number = f"  {item.file_name}:{item.line_number}"
        result.append(
            f"{file_name_and_line_number:<25}" f" > {item.func_name:<10} | {item.line}"
        )

    return "\n".join(result)
