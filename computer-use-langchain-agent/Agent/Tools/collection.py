from typing import Any, Dict, List
from .base import BaseAnthropicTool, ToolResult
from .computer import ComputerTool
from .edit import EditTool
from .bash import BashTool

class ToolCollection:
    """Collection of computer use tools."""
    
    def __init__(self, computer_tool: ComputerTool, bash_tool: BashTool, edit_tool: EditTool):
        self.tools = {
            computer_tool.name: computer_tool,
            bash_tool.name: bash_tool,
            edit_tool.name: edit_tool,
        }

    def to_params(self) -> List[Dict[str, Any]]:
        """Convert all tools to API parameters."""
        return [tool.to_params() for tool in self.tools.values()]

    async def run(self, name: str, tool_input: Dict[str, Any]) -> ToolResult:
        """Run a tool by name with given input."""
        if name not in self.tools:
            return ToolResult(
                output=None,
                error=f"Unknown tool: {name}",
                base64_image=None,
                system=None
            )
        
        try:
            # Pass tool_input directly without extracting action
            result = await self.tools[name](**tool_input)
            if isinstance(result, dict):
                return ToolResult(
                    output=result.get("output"),
                    error=result.get("error"),
                    base64_image=result.get("base64_image"),
                    system=result.get("system")
                )
            return result
        except Exception as e:
            return ToolResult(
                output=None,
                error=str(e),
                base64_image=None,
                system=None
            )
