"""Tool for editing files."""

import os
from pathlib import Path
from typing import ClassVar, Literal, Optional, TypedDict

from .base import BaseAnthropicTool, CLIResult, ToolError
from .run import run

SNIPPET_LINES = 3


class ToolEditParam(TypedDict):
    type: str
    name: str


class EditTool(BaseAnthropicTool):
    """
    A tool that allows the agent to edit files.
    The tool parameters are defined by Anthropic and are not editable.
    """

    name: ClassVar[Literal["str_replace_editor"]] = "str_replace_editor"
    api_type: ClassVar[Literal["text_editor_20241022"]] = "text_editor_20241022"  # Updated to match expected type
    _file_history: dict[Path, list[str]]

    def __init__(self):
        self._file_history = {}
        super().__init__()

    def validate_path(self, command: str, path: Path):
        """
        Check that the path/command combination is valid.
        """
        if not path.is_absolute():
            suggested_path = Path(os.getcwd()) / path
            raise ToolError(
                f"The path {path} is not an absolute path. Maybe you meant {suggested_path}?"
            )

        if command != "create" and not path.exists():
            raise ToolError(f"The path {path} does not exist")

        if command == "create" and path.exists():
            raise ToolError(f"File already exists at {path}")

        if command != "view" and path.is_dir():
            raise ToolError(f"The path {path} is a directory")

    async def __call__(
        self,
        *,
        command: str,
        path: str,
        old_str: str | None = None,
        new_str: str | None = None,
        file_text: str | None = None,
        insert_line: int | None = None,
        view_range: list[int] | None = None,
        **kwargs,
    ):
        path = Path(path)
        self.validate_path(command, path)

        if command == "view":
            if path.is_dir():
                # For directories, list contents using platform-appropriate method
                if os.name == 'nt':  # Windows
                    _, stdout, stderr = await run(
                        f'dir /B "{path}"'
                    )
                else:  # Unix
                    _, stdout, stderr = await run(
                        rf"find {path} -maxdepth 2 -not -path '*/\.*'"
                    )
                if not stderr:
                    stdout = f"Here's the files and directories in {path}:\n{stdout}\n"
                return CLIResult(output=stdout, error=stderr)

            file_content = path.read_text()

            if view_range:
                if len(view_range) != 2:
                    raise ToolError(
                        "The `view_range` parameter must be a list of two integers"
                    )
                init_line, final_line = view_range
                if init_line > final_line:
                    raise ToolError(
                        "Invalid `view_range`: first number must be less than or equal to second number"
                    )
                file_lines = file_content.split("\n")
                n_lines_file = len(file_lines)
                if final_line == -1:
                    file_content = "\n".join(file_lines[init_line - 1 :])
                else:
                    file_content = "\n".join(file_lines[init_line - 1 : final_line])

            return self._format_file_content(path, file_content, init_line=view_range[0] if view_range else 1)

        if command == "create":
            if file_text is None:
                raise ToolError("Parameter `file_text` is required for create command")

            path.write_text(file_text)
            return CLIResult(output=f"File {path} has been created.")

        if command == "str_replace":
            if old_str is None or new_str is None:
                raise ToolError(
                    "Parameters `old_str` and `new_str` are required for str_replace command"
                )

            file_content = path.read_text()
            occurrences = file_content.count(old_str)

            if occurrences == 0:
                raise ToolError(f"String '{old_str}' not found in {path}")

            if occurrences > 1:
                file_content_lines = file_content.split("\n")
                lines = [
                    f"{i+1}: {line}"
                    for i, line in enumerate(file_content_lines)
                    if old_str in line
                ]
                raise ToolError(
                    f"Found {occurrences} occurrences of '{old_str}' in {path}. Please be more specific.\nLines containing the string:\n"
                    + "\n".join(lines)
                )

            new_file_content = file_content.replace(old_str, new_str, 1)
            self._file_history.setdefault(path, []).append(file_content)
            path.write_text(new_file_content)

            # Create a snippet of the edited section
            replacement_line = file_content.split(old_str)[0].count("\n")
            start_line = max(0, replacement_line - SNIPPET_LINES)
            end_line = replacement_line + SNIPPET_LINES + new_str.count("\n")
            snippet = "\n".join(new_file_content.split("\n")[start_line : end_line + 1])

            return CLIResult(
                output=f"File {path} has been edited. Here's the affected section:\n{snippet}"
            )

        if command == "insert":
            if new_str is None:
                raise ToolError("Parameter `new_str` is required for insert command")
            if insert_line is None:
                raise ToolError("Parameter `insert_line` is required for insert command")

            new_str = new_str.expandtabs()
            file_text = path.read_text()
            file_text_lines = file_text.split("\n")
            n_lines_file = len(file_text_lines)

            if insert_line < 0 or (
                insert_line > n_lines_file and insert_line != n_lines_file
            ):
                raise ToolError(
                    f"Invalid `insert_line` parameter: {insert_line}. File has {n_lines_file} lines."
                )

            new_str_lines = new_str.split("\n")
            new_file_text_lines = (
                file_text_lines[:insert_line]
                + new_str_lines
                + file_text_lines[insert_line:]
            )
            new_file_text = "\n".join(new_file_text_lines)

            self._file_history.setdefault(path, []).append(file_text)
            path.write_text(new_file_text)

            # Create a snippet of the edited section
            start_line = max(0, insert_line - SNIPPET_LINES)
            end_line = min(
                len(new_file_text_lines),
                insert_line + len(new_str_lines) + SNIPPET_LINES,
            )
            snippet_lines = new_file_text_lines[start_line:end_line]
            snippet = "\n".join(snippet_lines)

            return CLIResult(
                output=f"File {path} has been edited. Here's the affected section:\n{snippet}"
            )

        if command == "undo_edit":
            if path not in self._file_history or not self._file_history[path]:
                raise ToolError(f"No edit history found for {path}")

            last_content = self._file_history[path].pop()
            path.write_text(last_content)

            return CLIResult(output=f"Last edit to {path} undone successfully")

        raise ToolError(f"Invalid command: {command}")

    def _format_file_content(
        self, path: Path, file_content: str, init_line: int = 1
    ) -> CLIResult:
        """Format file content with line numbers."""
        if not file_content:
            return CLIResult(output=f"File {path} is empty")

        file_descriptor = f"lines {init_line}-{init_line + file_content.count(chr(10))} of {path}"
        if init_line == 1 and file_content.count(chr(10)) == path.read_text().count(
            chr(10)
        ):
            file_descriptor = str(path)

        if file_content:
            file_content = file_content.expandtabs()
            file_content = "\n".join(
                [
                    f"{i + init_line:6}\t{line}"
                    for i, line in enumerate(file_content.split("\n"))
                ]
            )

        return CLIResult(
            output=(
                f"Here's the content of {file_descriptor}:\n"
                + file_content
                + "\n"
            )
        )

    def to_params(self) -> ToolEditParam:
        return {
            "type": self.api_type,
            "name": self.name,
        }
