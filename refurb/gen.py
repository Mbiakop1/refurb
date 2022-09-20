import os
import sys
from contextlib import suppress
from pathlib import Path
from subprocess import PIPE, run

from ._visitor_mappings import MAPPINGS

FILE_TEMPLATE = '''\
from dataclasses import dataclass

from mypy.nodes import {node_type}

from refurb.error import Error


@dataclass
class Error{error_name}(Error):
    """
    TODO: fill this in

    Bad:

    ```
    # TODO: fill this in
    ```

    Good:

    ```
    # TODO: fill this in
    ```
    """

    code = 999
    msg: str = "Your message here"


def check(node: {node_type}, errors: list[Error]) -> None:
    match node:
        case {node_type}():
            errors.append(Error{error_name}(node.line, node.column))
'''


def fzf(data: list[str] | None, args: list[str] = []) -> str:
    env = os.environ | {
        "SHELL": "/bin/bash",
        "FZF_DEFAULT_COMMAND": "find refurb -name '*.py' -not -path '*__*' > /dev/null 2>&1 | true",  # noqa: E501
    }

    process = run(
        ["fzf", "--height=20"] + args,
        env=env,
        stdout=PIPE,
        input=bytes("\n".join(data), "utf8") if data else None,
    )

    fzf_error_codes = (2, 130)

    if process.returncode in fzf_error_codes:
        sys.exit(1)

    return process.stdout[:-1].decode()


def folders_needing_init_file(path: Path) -> list[Path]:
    path = path.resolve()
    cwd = Path.cwd().resolve()

    if path.is_relative_to(cwd):
        to_remove = len(cwd.parents) + 1

        return [path, *list(path.parents)[:-to_remove]]

    return []


def main() -> None:
    node_type = fzf([x.__name__ for x in MAPPINGS.values()])

    file = Path(
        fzf(
            None, args=["--print-query", "--query", "refurb/checks/"]
        ).splitlines()[-1]
    )

    if file.suffix != ".py":
        print('refurb: File must end in ".py"')
        sys.exit(1)

    error_name = "".join(x.capitalize() for x in file.stem.split("_"))

    template = FILE_TEMPLATE.format(node_type=node_type, error_name=error_name)

    with suppress(FileExistsError):
        file.parent.mkdir(parents=True, exist_ok=True)

        for folder in folders_needing_init_file(file.parent):
            (folder / "__init__.py").touch(exist_ok=True)

    file.write_text(template)

    print(f"Generated {file}")


if __name__ == "__main__":
    main()