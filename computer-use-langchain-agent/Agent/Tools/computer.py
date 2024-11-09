import base64
import io
from enum import StrEnum
from typing import Literal, TypedDict, Optional
from uuid import uuid4

import pyautogui
from PIL import ImageGrab
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .base import ToolResult

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

class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"

class ComputerInput(BaseModel):
    action: Action = Field(description="The action to perform")
    text: Optional[str] = Field(None, description="Text for typing or key commands")
    coordinate: Optional[tuple[int, int]] = Field(None, description="(x, y) coordinates for mouse movement")

class ComputerTool(BaseTool):
    """Windows-compatible tool for screen, keyboard, and mouse interactions."""
    name: str = "computer"
    description: str = "Use a mouse and keyboard to interact with a computer, and take screenshots"
    args_schema: type[BaseModel] = ComputerInput
    screen_width: int = Field(default=0)
    screen_height: int = Field(default=0)
    screenshot_delay: float = Field(default=0.5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Get screen resolution
        self.screen_width, self.screen_height = pyautogui.size()

    def _run(self, action: Action, text: Optional[str] = None, coordinate: Optional[tuple[int, int]] = None) -> ToolResult:
        try:
            if action in ("mouse_move", "left_click_drag"):
                if not coordinate:
                    return ToolResult(
                        output=None,
                        error="coordinate is required for mouse actions",
                        base64_image=None,
                        system=None
                    )
                x, y = coordinate[0], coordinate[1]
                
                if action == "mouse_move":
                    pyautogui.moveTo(x, y)
                else:  # left_click_drag
                    pyautogui.dragTo(x, y)

            elif action in ("key", "type"):
                if not text:
                    return ToolResult(
                        output=None,
                        error="text is required for keyboard actions",
                        base64_image=None,
                        system=None
                    )
                
                if action == "key":
                    pyautogui.press(text)
                else:  # type
                    pyautogui.write(text)

            elif action in ("left_click", "right_click", "middle_click", "double_click"):
                button = {
                    "left_click": "left",
                    "right_click": "right",
                    "middle_click": "middle",
                }
                if action == "double_click":
                    pyautogui.doubleClick()
                else:
                    pyautogui.click(button=button.get(action, "left"))

            elif action == "screenshot":
                return self.take_screenshot()

            elif action == "cursor_position":
                x, y = pyautogui.position()
                return ToolResult(
                    output=f"X={x},Y={y}",
                    error=None,
                    base64_image=None,
                    system=None
                )

            # Take a screenshot after any action that changes the screen
            if action != "cursor_position":
                return self.take_screenshot()

            return ToolResult(
                output="Action completed",
                error=None,
                base64_image=None,
                system=None
            )

        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Action failed: {str(e)}",
                base64_image=None,
                system=None
            )

    async def _arun(self, action: Action, text: Optional[str] = None, coordinate: Optional[tuple[int, int]] = None) -> ToolResult:
        return self._run(action, text, coordinate)

    def take_screenshot(self) -> ToolResult:
        """Take a screenshot using PIL's ImageGrab."""
        try:
            # Capture the screen
            screenshot = ImageGrab.grab()
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            base64_image = base64.b64encode(img_byte_arr).decode()

            return ToolResult(
                output="Screenshot taken successfully",
                error=None,
                base64_image=base64_image,
                system=None
            )
        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Screenshot failed: {str(e)}",
                base64_image=None,
                system=None
            )
