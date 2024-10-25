"""Utilities for running shell commands."""

import asyncio
import platform

TRUNCATED_MESSAGE: str = "<response clipped><NOTE>To save on context, only part of this file has been shown. You should use appropriate search/filter commands for your platform to find specific content.</NOTE>"
MAX_RESPONSE_LEN: int = 16000


async def run(cmd: str, timeout: float = 30.0):
    """Run a shell command asynchronously with a timeout."""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
    except asyncio.TimeoutError:
        process.kill()
        return (
            process.returncode,
            "",
            f"Command timed out after {timeout} seconds",
        )

    stdout_str = stdout.decode() if stdout else ""
    stderr_str = stderr.decode() if stderr else ""

    if len(stdout_str) > MAX_RESPONSE_LEN:
        stdout_str = stdout_str[:MAX_RESPONSE_LEN] + "\n" + TRUNCATED_MESSAGE

    return process.returncode, stdout_str, stderr_str
