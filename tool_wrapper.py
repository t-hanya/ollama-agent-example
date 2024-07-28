"""
Tool wrapper to support following features.

- Construct tool document for ollama's tools input.
- Tool argument validation with Pydantic.
"""

import inspect
from typing import Annotated
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class Tool:
    """A tool wrapper to provide tool doc and argument validation."""

    def __init__(self,
                 func: callable,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 args_schema: Optional[type[BaseModel]] = None
                ) -> None:
        self.func = func
        self.name = name
        self.description = description
        self.args_schema = args_schema

    def __call__(self, *args: tuple, **kwargs: dict) -> Any:
        return self.func(*args, **kwargs)
