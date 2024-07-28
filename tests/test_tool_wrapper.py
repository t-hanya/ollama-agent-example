from tool_wrapper import Tool


class TestTool:

    def test(self) -> None:

        def _add_numbers(a: int, b: int) -> int:
            return a + b

        tool = Tool(
            _add_numbers,
            name='add_numbers',
            description='Calculate a + b'
        )

        assert tool.name == 'add_numbers'
        assert tool.description == 'Calculate a + b'

        ret = tool(10, 20)
        assert ret == 30

        # api doc
        api_doc = tool.api_doc['function']
        assert api_doc['name'] == 'add_numbers'
        assert api_doc['description'] == 'Calculate a + b'
        assert api_doc['parameters']['properties']['a']['type'] == 'integer'
        assert api_doc['parameters']['properties']['b']['type'] == 'integer'
