"""Tool for executing shell commands."""

import asyncio
import os
import platform
import subprocess
import threading
from queue import Queue
from typing import ClassVar, Literal

from anthropic.types.beta import BetaToolBash20241022Param

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class _WindowsShellSession:
    """A Windows-specific shell session using cmd.exe."""
    def __init__(self):
        self._started = False
        self._timed_out = False
        self._process = None
        self._output_queue = Queue()
        self._error_queue = Queue()
        self._timeout = 120.0
        self._sentinel = "<<exit>>"

    async def start(self):
        if self._started:
            return

        # Start cmd.exe process
        self._process = subprocess.Popen(
            "cmd.exe",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        # Start threads to read output and error streams
        self._start_output_reader()
        self._start_error_reader()
        
        self._started = True

    def _start_output_reader(self):
        def reader():
            while True:
                line = self._process.stdout.readline()
                if not line:
                    break
                self._output_queue.put(line)
        
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()

    def _start_error_reader(self):
        def reader():
            while True:
                line = self._process.stderr.readline()
                if not line:
                    break
                self._error_queue.put(line)
        
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()

    def stop(self):
        """Terminate the shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.poll() is not None:
            return
        self._process.terminate()

    async def run(self, command: str):
        """Execute a command in the shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.poll() is not None:
            return ToolResult(
                system="tool must be restarted",
                error=f"shell has exited with returncode {self._process.returncode}",
            )

        # Clear queues
        while not self._output_queue.empty():
            self._output_queue.get()
        while not self._error_queue.empty():
            self._error_queue.get()

        # Send command with sentinel
        self._process.stdin.write(f"{command} & echo {self._sentinel}\n")
        self._process.stdin.flush()

        # Read output until sentinel
        output_lines = []
        error_lines = []
        timeout = self._timeout
        start_time = asyncio.get_event_loop().time()

        while True:
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                self._timed_out = True
                raise ToolError(
                    f"timed out: shell has not returned in {timeout} seconds and must be restarted"
                )

            # Check for output
            try:
                line = self._output_queue.get_nowait()
                if self._sentinel in line:
                    break
                output_lines.append(line)
            except:
                pass

            # Check for errors
            try:
                line = self._error_queue.get_nowait()
                error_lines.append(line)
            except:
                pass

            # Small delay to prevent busy waiting
            await asyncio.sleep(0.1)

        output = "".join(output_lines).strip()
        error = "".join(error_lines).strip()

        return CLIResult(output=output, error=error)


class _UnixShellSession:
    """A Unix-specific shell session using bash."""

    def __init__(self):
        self._started = False
        self._timed_out = False
        self._timeout: float = 120.0
        self._sentinel: str = "<<exit>>"
        self._output_delay: float = 0.2

    async def start(self):
        if self._started:
            return

        self._process = await asyncio.create_subprocess_shell(
            "/bin/bash",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=os.setsid,
        )
        self._started = True

    def stop(self):
        """Terminate the shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            return
        self._process.terminate()

    async def run(self, command: str):
        """Execute a command in the shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            return ToolResult(
                system="tool must be restarted",
                error=f"shell has exited with returncode {self._process.returncode}",
            )
        if self._timed_out:
            raise ToolError(
                f"timed out: shell has not returned in {self._timeout} seconds and must be restarted",
            )

        assert self._process.stdin
        assert self._process.stdout
        assert self._process.stderr

        self._process.stdin.write(
            command.encode() + f"; echo '{self._sentinel}'\n".encode()
        )
        await self._process.stdin.drain()

        try:
            async with asyncio.timeout(self._timeout):
                while True:
                    await asyncio.sleep(self._output_delay)
                    output = self._process.stdout._buffer.decode()
                    if self._sentinel in output:
                        output = output[: output.index(self._sentinel)]
                        break
        except asyncio.TimeoutError:
            self._timed_out = True
            raise ToolError(
                f"timed out: shell has not returned in {self._timeout} seconds and must be restarted",
            ) from None

        if output.endswith("\n"):
            output = output[:-1]

        error = self._process.stderr._buffer.decode()
        if error.endswith("\n"):
            error = error[:-1]

        self._process.stdout._buffer.clear()
        self._process.stderr._buffer.clear()

        return CLIResult(output=output, error=error)


class BashTool(BaseAnthropicTool):
    """
    A tool that allows the agent to run shell commands.
    The tool parameters are defined by Anthropic and are not editable.
    """

    _session: _WindowsShellSession | _UnixShellSession | None
    name: ClassVar[Literal["bash"]] = "bash"
    api_type: ClassVar[Literal["bash_20241022"]] = "bash_20241022"

    def __init__(self):
        self._session = None
        super().__init__()

    async def __call__(
        self, command: str | None = None, restart: bool = False, **kwargs
    ):
        if restart:
            if self._session:
                self._session.stop()
            self._session = _WindowsShellSession() if platform.system() == "Windows" else _UnixShellSession()
            await self._session.start()
            return ToolResult(system="tool has been restarted.")

        if self._session is None:
            self._session = _WindowsShellSession() if platform.system() == "Windows" else _UnixShellSession()
            await self._session.start()

        if command is not None:
            return await self._session.run(command)

        raise ToolError("no command provided.")

    def to_params(self) -> BetaToolBash20241022Param:
        return {
            "type": self.api_type,
            "name": self.name,
        }
