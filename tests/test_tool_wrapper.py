from typing import Annotated

from pydantic import BaseModel
from pydantic import Field

from tool_wrapper import Tool


class TestTool:

    def test_explicit_attributes(self) -> None:

        def _add_numbers(a: int, b: int) -> int:
            return a + b

        class AddNumbersInput(BaseModel):
            a: int = Field(..., description='First number')
            b: int = Field(..., description='Second number')

        tool = Tool(
            _add_numbers,
            name='add_numbers',
            description='Calculate a + b',
            args_schema=AddNumbersInput
        )

        assert tool.name == 'add_numbers'
        assert tool.description == 'Calculate a + b'

        ret = tool(10, 20)
        assert ret == 30

        # api doc
        api_doc = tool.api_doc['function']
        assert api_doc['name'] == 'add_numbers'
        assert api_doc['description'] == 'Calculate a + b'

        props = api_doc['parameters']['properties']
        assert props['a']['type'] == 'integer'
        assert props['a']['description'] == 'First number'
        assert props['b']['type'] == 'integer'
        assert props['b']['description'] == 'Second number'

    def test_implicit_attributes(self) -> None:

        def _add_numbers(a: Annotated[int, 'First number'],
                         b: Annotated[int, 'Second number'] = 0,
                        ) -> int:
            """Add two numbers."""
            pass

        tool = Tool(_add_numbers)

        assert tool.name == '_add_numbers'
        assert tool.description == 'Add two numbers.'

        props = tool.api_doc['function']['parameters']['properties']
        assert props['a']['type'] == 'integer'
        assert props['a']['description'] == 'First number'
        assert props['b']['type'] == 'integer'
        assert props['b']['description'] == 'Second number'
        assert props['b']['default'] == 0
        assert tool.api_doc['function']['parameters']['required'] == ['a']
