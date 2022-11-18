"""Defines different text for display used throughout the app"""

from flet import (
    Text,
)
from res import fonts, colors
from core.ui.utils.flet_constants import TXT_ALIGN_LEFT, START_ALIGNMENT


def get_error_txt(
    txt: str,
    size: int = fonts.BODY_2_SIZE,
    color: str = colors.ERROR_COLOR,
    show: bool = True,
):
    """Displays text formatted for errors / warnings"""
    return Text(txt, color=color, size=size, visible=show)