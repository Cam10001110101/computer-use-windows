from typing import Optional, TypedDict

class ToolResult(TypedDict):
    """Result from a tool execution."""
    output: Optional[str]
    error: Optional[str]
    base64_image: Optional[str]
    system: Optional[str]

class ToolError(Exception):
    """Exception raised for tool errors."""
    def __init__(self, message: str = "", output: str = ""):
        self.message = message
        self.output = output
        super().__init__(message or output)

    def to_result(self) -> ToolResult:
        """Convert error to a ToolResult."""
        return ToolResult(
            output=self.output,
            error=self.message or self.output,
            base64_image=None,
            system=None
        )

class BaseAnthropicTool:
    """Base class for Anthropic tools."""
    name: str
    api_type: str

    def __init__(self):
        self.__name__ = self.name  # Required for LangChain compatibility

    def to_params(self):
        """Convert tool parameters to Anthropic API format."""
        return {"name": self.name, "type": self.api_type}

    def handle_error(self, e: Exception) -> ToolResult:
        """Convert any exception to a ToolResult."""
        if isinstance(e, ToolError):
            return e.to_result()
        return ToolResult(
            output=None,
            error=str(e),
            base64_image=None,
            system=None
        )
