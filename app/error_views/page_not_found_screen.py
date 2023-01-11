from core.abstractions import TuttleView
from typing import Callable
from flet import UserControl, Column, Container, padding
from core.utils import CENTER_ALIGNMENT
from core.views import get_error_txt, get_primary_btn
from core.abstractions import TuttleViewParams
from res.dimens import SPACE_MD, SPACE_STD


class Error404Screen(TuttleView, UserControl):
    def __init__(self, params: TuttleViewParams):
        super().__init__(params)
        self.vertical_alignment_in_parent = CENTER_ALIGNMENT
        self.horizontal_alignment_in_parent = CENTER_ALIGNMENT

    def build(self):
        view = Container(
            Column(
                expand=True,
                spacing=SPACE_STD,
                run_spacing=SPACE_STD,
                controls=[
                    get_error_txt("OOps! Looks like you took a wrong turn"),
                    get_primary_btn(
                        label="Go Back".upper(), on_click=self.on_navigate_back
                    ),
                ],
            ),
            padding=padding.all(SPACE_MD),
        )

        return view