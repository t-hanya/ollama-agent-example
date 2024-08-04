"""
Tool wrapper to support following features.

- Construct tool document for ollama's tools input.
- Tool argument validation with Pydantic.
"""

import inspect
import typing
from typing import Annotated
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import create_model


def _get_name(func: callable) -> str:
    if hasattr(func, '__name__'):
        return func.__name__
    else:
        return func.__class__.__name__


def annotations_to_schema(func: callable) -> BaseModel:
    """Construct function argument model from type annotation.

    Argument description is assumed to be the following form::

        def add(a: typing.Annotated[int, 'The first number'],
                b: typing.Annotated[int, 'The second number']) -> int:
            pass
    """

    params = inspect.signature(func).parameters
    param_specs = {}
    for param in params.values():
        # check type annotation is available
        if param.annotation is inspect._empty:
            raise ValueError(
                'All params should be type annotated (func: {}, param: {}).'.foramt(
                    func.__name__,
                    param.name
                )
            )

        # get default value
        if param.default is inspect._empty:
            default = ...
        else:
            default = param.default

        # get type and description
        desc = None
        if typing.get_origin(param.annotation) is Annotated:
            annt_args = typing.get_args(param.annotation)
            type_ = annt_args[0]
            for arg in annt_args[1:]:
                if type(arg) is str:
                    desc = arg
                    break
        else:
            type_ = param.annotation

        param_specs[param.name] = (type_, Field(default, description=desc))

    # my_func => MyFuncModel
    name_blocks = _get_name(func).split('_')
    model_name = '_' + ''.join([block.capitalize() for block in name_blocks]) + 'Model'

    return create_model(model_name, **param_specs)


def _remove_key_recursively(data: dict, key: str) -> dict:
    if isinstance(data, dict):
        keys = list(data.keys())
        for k in keys:
            if k == key and "type" in data:
                del data[k]
            else:
                _remove_key_recursively(data[k], key)
    return data


def construct_tool_doc(name: str,
                       description: str,
                       args_spec: type[BaseModel]
                      ) -> dict:
    """Construct tool API document."""
    schema = args_spec.model_json_schema()
    props = schema['properties']
    props = _remove_key_recursively(props, key='title')

    doc = {
        'type': 'function',
        'function': {
            'name': name,
            'description': description,
            'parameters': {
                'type': 'object',
                'properties': props,
            }
        }
    }
    if props:
        doc['function']['parameters']['required'] = schema['required']
    return doc


class Tool:
    """A tool wrapper to provide tool doc and argument validation."""

    def __init__(self,
                 func: callable,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 args_schema: Optional[type[BaseModel]] = None
                ) -> None:
        self.func = func
        self.name = name or _get_name(func)
        self.description = description or func.__doc__

        if args_schema is None:
            args_schema = annotations_to_schema(func)
        self.args_schema = args_schema
        self.signature = inspect.signature(func)

    def __call__(self, *args: tuple, **kwargs: dict) -> Any:
        bound_args = self.signature.bind(*args, **kwargs).arguments
        inputs = self.args_schema(**bound_args)
        return self.func(**inputs.model_dump())

    @property
    def api_doc(self) -> dict:
        """Tool API document."""
        return construct_tool_doc(self.name,
                                  self.description,
                                  self.args_schema)
