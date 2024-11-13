from datetime import datetime
from typing import Optional
from langchain.tools import BaseTool
from pydantic import BaseModel

from .base import ToolResult

class DateTimeInput(BaseModel):
    format: Optional[str] = None

class DateTimeTool(BaseTool):
    """Tool for getting the current date and time."""
    name: str = "datetime"
    description: str = "Get the current date and time. Optionally specify a format string."
    args_schema: type[BaseModel] = DateTimeInput

    def _run(
        self,
        format: Optional[str] = None,
    ) -> ToolResult:
        try:
            current_time = datetime.now()
            
            if format:
                try:
                    formatted_time = current_time.strftime(format)
                except ValueError as e:
                    return ToolResult(
                        output=None,
                        error=f"Invalid format string: {str(e)}",
                        base64_image=None,
                        system=None
                    )
            else:
                # Default format: YYYY-MM-DD HH:MM:SS
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            return ToolResult(
                output=formatted_time,
                error=None,
                base64_image=None,
                system=None
            )

        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Failed to get date/time: {str(e)}",
                base64_image=None,
                system=None
            )

    async def _arun(
        self,
        format: Optional[str] = None,
    ) -> ToolResult:
        # For datetime operations, async implementation can just call sync version
        return self._run(format=format)
