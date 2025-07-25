from typing import Any, Protocol

from new_python_github_project.config import Config

# NOTE: These type aliases cannot start with "Test" because then pytest will
#       believe that they are test classes, see https://stackoverflow.com/q/76689604/2173773

PytestDataDict = dict[str, str]
QtBot = Any  # Missing type hints here


class GetConfig(Protocol):  # pragma: no cover
    def __call__(self) -> Config: ...
