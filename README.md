# ollama agent examples

## `app.py`: ollama tool use example with Streamlit

```bash
streamlit run app.py
```

## `tool_wrapper.py`: Utility to construct tool json schema

```python
import json
from typing import Annotated

from tool_wrapper import Tool


def add(num1: Annotated[int, 'First number'],
        num2: Annotated[int, 'Second number']
       ) -> int:
    """Calculate `num1 + num2` and return the result."""
    return num1 + num2


tool = Tool(add)
print(json.dumps(tool.api_doc, indent=2))
```

Output:
```json
{
  "type": "function",
  "function": {
    "name": "add",
    "description": "Calculate `num1 + num2` and return the result.",
    "parameters": {
      "type": "object",
      "properties": {
        "num1": {
          "description": "First number",
          "type": "integer"
        },
        "num2": {
          "description": "Second number",
          "type": "integer"
        }
      },
      "required": [
        "num1",
        "num2"
      ]
    }
  }
}
```

