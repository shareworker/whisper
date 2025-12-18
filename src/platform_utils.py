import platform
import shutil
from enum import Enum
from typing import Optional


class Platform(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    UNKNOWN = "unknown"


def get_platform() -> Platform:
    system = platform.system().lower()
    if system == "windows":
        return Platform.WINDOWS
    elif system == "linux":
        return Platform.LINUX
    return Platform.UNKNOWN


def is_windows() -> bool:
    return get_platform() == Platform.WINDOWS


def is_linux() -> bool:
    return get_platform() == Platform.LINUX


def check_external_tool(tool_name: str) -> Optional[str]:
    """Check if an external tool is available in PATH.
    
    Returns the path to the tool if found, None otherwise.
    """
    return shutil.which(tool_name)


def check_required_tools() -> dict[str, bool]:
    """Check availability of required external tools.
    
    Returns a dict mapping tool name to availability status.
    """
    tools = ["ffmpeg", "yt-dlp"]
    return {tool: check_external_tool(tool) is not None for tool in tools}
