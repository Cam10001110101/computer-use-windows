from pathlib import Path
from typing import Literal, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .base import ToolResult

class EditInput(BaseModel):
    command: Literal["view", "create", "str_replace", "insert"] = Field(
        description="The command to run"
    )
    path: str = Field(description="Path to file or directory")
    file_text: Optional[str] = Field(None, description="Text content for file operations")
    old_str: Optional[str] = Field(None, description="String to replace")
    new_str: Optional[str] = Field(None, description="Replacement string")
    insert_line: Optional[int] = Field(None, description="Line number for insertion")
    view_range: Optional[list[int]] = Field(None, description="Range of lines to view [start, end]")

class EditTool(BaseTool):
    """Windows-compatible tool for file operations."""
    name: str = "str_replace_editor"
    description: str = "Custom editing tool for viewing, creating and editing files"
    args_schema: type[BaseModel] = EditInput

    def _run(
        self,
        command: str,
        path: str,
        file_text: Optional[str] = None,
        old_str: Optional[str] = None,
        new_str: Optional[str] = None,
        insert_line: Optional[int] = None,
        view_range: Optional[list[int]] = None,
    ) -> ToolResult:
        try:
            file_path = Path(path)

            if command == "view":
                if not file_path.exists():
                    return ToolResult(
                        output=None,
                        error=f"File not found: {path}",
                        base64_image=None,
                        system=None
                    )
                content = file_path.read_text(encoding='utf-8')
                if view_range:
                    lines = content.splitlines()
                    start, end = view_range
                    content = '\n'.join(lines[start:end+1])
                return ToolResult(
                    output=content,
                    error=None,
                    base64_image=None,
                    system=None
                )

            elif command == "create":
                if not file_text:
                    return ToolResult(
                        output=None,
                        error="file_text is required for create command",
                        base64_image=None,
                        system=None
                    )
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(file_text, encoding='utf-8')
                return ToolResult(
                    output=f"File created successfully: {path}",
                    error=None,
                    base64_image=None,
                    system=None
                )

            elif command == "str_replace":
                if not all([old_str, new_str]):
                    return ToolResult(
                        output=None,
                        error="old_str and new_str are required for str_replace",
                        base64_image=None,
                        system=None
                    )
                if not file_path.exists():
                    return ToolResult(
                        output=None,
                        error=f"File not found: {path}",
                        base64_image=None,
                        system=None
                    )
                content = file_path.read_text(encoding='utf-8')
                new_content = content.replace(old_str, new_str)
                file_path.write_text(new_content, encoding='utf-8')
                return ToolResult(
                    output=f"String replaced successfully in {path}",
                    error=None,
                    base64_image=None,
                    system=None
                )

            elif command == "insert":
                if not file_text or insert_line is None:
                    return ToolResult(
                        output=None,
                        error="file_text and insert_line are required for insert",
                        base64_image=None,
                        system=None
                    )
                if not file_path.exists():
                    return ToolResult(
                        output=None,
                        error=f"File not found: {path}",
                        base64_image=None,
                        system=None
                    )
                
                lines = file_path.read_text(encoding='utf-8').splitlines()
                if insert_line < 0:
                    insert_line = len(lines) + insert_line + 1
                lines.insert(insert_line, file_text)
                file_path.write_text('\n'.join(lines), encoding='utf-8')
                return ToolResult(
                    output=f"Text inserted successfully at line {insert_line} in {path}",
                    error=None,
                    base64_image=None,
                    system=None
                )

            else:
                return ToolResult(
                    output=None,
                    error=f"Unknown command: {command}",
                    base64_image=None,
                    system=None
                )

        except Exception as e:
            return ToolResult(
                output=None,
                error=f"File operation failed: {str(e)}",
                base64_image=None,
                system=None
            )

    async def _arun(
        self,
        command: str,
        path: str,
        file_text: Optional[str] = None,
        old_str: Optional[str] = None,
        new_str: Optional[str] = None,
        insert_line: Optional[int] = None,
        view_range: Optional[list[int]] = None,
    ) -> ToolResult:
        return self._run(
            command=command,
            path=path,
            file_text=file_text,
            old_str=old_str,
            new_str=new_str,
            insert_line=insert_line,
            view_range=view_range
        )
