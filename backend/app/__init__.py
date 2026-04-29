"""智能旅行助手后端应用"""

import sys

__version__ = "1.0.0"


def _configure_windows_console() -> None:
    """避免Windows终端输出特殊字符时出现编码错误。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


_configure_windows_console()
