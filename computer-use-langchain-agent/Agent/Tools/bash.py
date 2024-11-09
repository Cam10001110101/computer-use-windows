import asyncio
import subprocess
from typing import Literal, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .base import ToolResult

class BashInput(BaseModel):
    command: str = Field(description="The command to execute")
    restart: Optional[bool] = Field(None, description="Whether to restart the tool")

class BashTool(BaseTool):
    """Windows-compatible tool for executing system commands."""
    name: str = "bash"
    description: str = "Run commands in a bash shell"
    args_schema: type[BaseModel] = BashInput

    def _run(
        self,
        command: str,
        restart: Optional[bool] = None,
    ) -> ToolResult:
        try:
            # Validate command
            if not self.validate_command(command):
                return ToolResult(
                    output=None,
                    error="Command contains forbidden operations",
                    base64_image=None,
                    system=None
                )

            # Convert Unix-style commands to Windows equivalents
            windows_command = self.convert_to_windows_command(command)
            
            # Run the command synchronously
            process = subprocess.run(
                windows_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if process.returncode != 0 and process.stderr:
                return ToolResult(
                    output=process.stdout,
                    error=process.stderr,
                    base64_image=None,
                    system=None
                )
            
            return ToolResult(
                output=process.stdout,
                error=None,
                base64_image=None,
                system=None
            )

        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Command execution failed: {str(e)}",
                base64_image=None,
                system=None
            )

    async def _arun(
        self,
        command: str,
        restart: Optional[bool] = None,
    ) -> ToolResult:
        try:
            # Validate command
            if not self.validate_command(command):
                return ToolResult(
                    output=None,
                    error="Command contains forbidden operations",
                    base64_image=None,
                    system=None
                )

            # Convert Unix-style commands to Windows equivalents
            windows_command = self.convert_to_windows_command(command)
            
            # Run the command
            process = await asyncio.create_subprocess_shell(
                windows_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            stdout, stderr = await process.communicate()
            
            # Decode output using UTF-8, ignoring errors
            stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else None
            stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else None
            
            if process.returncode != 0 and stderr_str:
                return ToolResult(
                    output=stdout_str,
                    error=stderr_str,
                    base64_image=None,
                    system=None
                )
            
            return ToolResult(
                output=stdout_str,
                error=None,
                base64_image=None,
                system=None
            )

        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Command execution failed: {str(e)}",
                base64_image=None,
                system=None
            )

    def convert_to_windows_command(self, command: str) -> str:
        """Convert Unix-style commands to Windows equivalents."""
        # Common Unix to Windows command mappings
        command_map = {
            'ls': 'dir',
            'rm': 'del',
            'cp': 'copy',
            'mv': 'move',
            'cat': 'type',
            'clear': 'cls',
            'touch': 'echo.>',
            'mkdir': 'md',
            'rmdir': 'rd',
            'pwd': 'cd',
            'grep': 'findstr',
        }

        # Split the command into parts
        parts = command.split()
        if not parts:
            return command

        # Replace the command if it exists in the mapping
        base_cmd = parts[0]
        if base_cmd in command_map:
            parts[0] = command_map[base_cmd]
            command = ' '.join(parts)

        # Handle path separators
        command = command.replace('/', '\\')
        
        return command

    def validate_command(self, command: str) -> bool:
        """Validate that the command is safe to execute."""
        # List of forbidden commands
        forbidden = [
            'format',
            'del /f',
            'rmdir /s',
            'rd /s',
            'del /q',
            'format',
            'shutdown',
            'taskkill',
        ]
        
        # Check if any forbidden command is present
        command_lower = command.lower()
        return not any(cmd in command_lower for cmd in forbidden)
