from traceback import extract_tb
from typing import List

from sshared.terminal.color import fg_color


def pretty_exception(exc: Exception) -> str:
    exc_summary = (
        f"{type(exc).__name__}({exc.args[0]!r})"
        if exc.args
        else f"{type(exc).__name__}"
    )
    result: List[str] = [f"{fg_color('Exception', 'RED')} {exc_summary}"]

    stack = extract_tb(exc.__traceback__)
    for item in stack:
        filename_and_lineno = f"  {item.filename.split('/')[-1]}:{item.lineno}"
        result.append(
            f"{filename_and_lineno:<25}"
            f" > {item.name:<10} | {item.line}"
        )

    return "\n".join(result)
