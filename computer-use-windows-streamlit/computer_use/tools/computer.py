"""Tool for computer interaction."""

import asyncio
import base64
import os
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict
from uuid import uuid4

import pyautogui
import win32api
import win32con
from PIL import Image
from anthropic.types.beta import BetaToolParam

from .base import BaseAnthropicTool, ToolError, ToolResult

# Configure pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Add small delay between actions

OUTPUT_DIR = os.path.join(os.environ.get('TEMP', '.'), 'outputs')

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
]

class Resolution(TypedDict):
    width: int
    height: int

# sizes above XGA/WXGA are not recommended (see README.md)
# scale down to one of these targets if ComputerTool._scaling_enabled is set
MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}

class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"

class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None

def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]

class ComputerTool(BaseAnthropicTool):
    """
    A tool that allows the agent to interact with the screen, keyboard, and mouse of the current computer.
    Windows-compatible implementation using pyautogui and win32api.
    """

    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"  # Updated to match expected type
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 2.0
    _scaling_enabled = True

    @property
    def options(self) -> ComputerToolOptions:
        width, height = self.scale_coordinates(
            ScalingSource.COMPUTER, self.width, self.height
        )
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_num,
        }

    def to_params(self) -> BetaToolParam:
        return {"name": self.name, "type": self.api_type, **self.options}

    def __init__(self):
        super().__init__()
        # Get primary monitor resolution
        self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.display_num = None  # Windows handles multiple displays differently

    async def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        try:
            if action in ("mouse_move", "left_click_drag"):
                if coordinate is None:
                    raise ToolError(f"coordinate is required for {action}")
                if text is not None:
                    raise ToolError(f"text is not accepted for {action}")
                if not isinstance(coordinate, list) or len(coordinate) != 2:
                    raise ToolError(f"{coordinate} must be a tuple of length 2")
                if not all(isinstance(i, int) and i >= 0 for i in coordinate):
                    raise ToolError(f"{coordinate} must be a tuple of non-negative ints")

                x, y = self.scale_coordinates(
                    ScalingSource.API, coordinate[0], coordinate[1]
                )

                if action == "mouse_move":
                    await asyncio.to_thread(pyautogui.moveTo, x, y)
                elif action == "left_click_drag":
                    await asyncio.to_thread(pyautogui.dragTo, x, y)

                return await self.screenshot()

            if action in ("key", "type"):
                if text is None:
                    raise ToolError(f"text is required for {action}")
                if coordinate is not None:
                    raise ToolError(f"coordinate is not accepted for {action}")
                if not isinstance(text, str):
                    raise ToolError(output=f"{text} must be a string")

                if action == "key":
                    await asyncio.to_thread(pyautogui.press, text)
                elif action == "type":
                    for chunk in chunks(text, TYPING_GROUP_SIZE):
                        await asyncio.to_thread(
                            pyautogui.write, chunk, interval=TYPING_DELAY_MS/1000
                        )

                return await self.screenshot()

            if action in (
                "left_click",
                "right_click",
                "double_click",
                "middle_click",
                "screenshot",
                "cursor_position",
            ):
                if text is not None:
                    raise ToolError(f"text is not accepted for {action}")
                if coordinate is not None:
                    raise ToolError(f"coordinate is not accepted for {action}")

                if action == "screenshot":
                    return await self.screenshot()
                elif action == "cursor_position":
                    x, y = win32api.GetCursorPos()
                    scaled_x, scaled_y = self.scale_coordinates(
                        ScalingSource.COMPUTER, x, y
                    )
                    return ToolResult(
                        output=f"X={scaled_x},Y={scaled_y}",
                        error=None,
                        base64_image=None
                    )
                else:
                    click_funcs = {
                        "left_click": lambda: pyautogui.click(button='left'),
                        "right_click": lambda: pyautogui.click(button='right'),
                        "middle_click": lambda: pyautogui.click(button='middle'),
                        "double_click": lambda: pyautogui.doubleClick(),
                    }
                    await asyncio.to_thread(click_funcs[action])
                    return await self.screenshot()

            raise ToolError(f"Invalid action: {action}")

        except pyautogui.FailSafeException as e:
            raise ToolError(f"Mouse movement failed (hit screen edge): {str(e)}")
        except Exception as e:
            raise ToolError(f"Action failed: {str(e)}")

    async def screenshot(self) -> ToolResult:
        """Take a screenshot of the current screen and return the base64 encoded image."""
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"

        try:
            # Take screenshot using pyautogui
            screenshot = await asyncio.to_thread(pyautogui.screenshot)
            
            if self._scaling_enabled:
                x, y = self.scale_coordinates(
                    ScalingSource.COMPUTER, self.width, self.height
                )
                screenshot = screenshot.resize((x, y), Image.Resampling.LANCZOS)

            # Save the screenshot
            screenshot.save(str(path))
            
            # Add delay to let things settle
            await asyncio.sleep(self._screenshot_delay)
            
            # Return the result with base64 encoded image
            return ToolResult(
                output=None,
                error=None,
                base64_image=base64.b64encode(path.read_bytes()).decode()
            )
        except Exception as e:
            raise ToolError(f"Failed to take screenshot: {str(e)}")
        finally:
            # Clean up the temporary file
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass

    def scale_coordinates(self, source: ScalingSource, x: int, y: int):
        """Scale coordinates to a target maximum resolution."""
        if not self._scaling_enabled:
            return x, y
        ratio = self.width / self.height
        target_dimension = None
        for dimension in MAX_SCALING_TARGETS.values():
            # allow some error in the aspect ratio - not ratios are exactly 16:9
            if abs(dimension["width"] / dimension["height"] - ratio) < 0.02:
                if dimension["width"] < self.width:
                    target_dimension = dimension
                break
        if target_dimension is None:
            return x, y
        # should be less than 1
        x_scaling_factor = target_dimension["width"] / self.width
        y_scaling_factor = target_dimension["height"] / self.height
        if source == ScalingSource.API:
            if x > self.width or y > self.height:
                raise ToolError(f"Coordinates {x}, {y} are out of bounds")
            # scale up
            return round(x / x_scaling_factor), round(y / y_scaling_factor)
        # scale down
        return round(x * x_scaling_factor), round(y * y_scaling_factor)
