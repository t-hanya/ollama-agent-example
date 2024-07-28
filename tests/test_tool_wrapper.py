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

