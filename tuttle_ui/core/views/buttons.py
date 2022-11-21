"""Defines main buttons used in app"""
from flet import ElevatedButton, ButtonStyle
from res.fonts import HEADLINE_FONT
from res import colors


def get_primary_btn(
    onClickCallback,
    label: str,
    width: int = 200,
):
    """An elevated button with primary styling"""
    style = ButtonStyle()
    return ElevatedButton(label, width=width, style=style, on_click=onClickCallback)