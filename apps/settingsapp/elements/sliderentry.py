#
# ╔═╗ ╔╗            ╔╗        ╔╗ ╔╗                 ╔══╗                  ╔═══╗     ╔╗
# ║║╚╗║║            ║║        ║║ ║║                 ╚╣╠╝                  ║╔═╗║    ╔╝╚╗
# ║╔╗╚╝║╔╗╔╗╔╗╔╗╔══╗╚╝╔══╗    ║╚═╝║╔╗ ╔╗╔══╗╔═╗      ║║ ╔══╗╔═╗ ╔╗╔══╗    ║╚══╗╔══╗╚╗╔╝╔╗╔╗╔══╗
# ║║╚╗║║╠╣╚╬╬╝╠╣║╔╗║  ║══╣    ║╔═╗║║║ ║║║╔╗║║╔╝╔═══╗ ║║ ║╔╗║║╔╗╗╠╣║══╣    ╚══╗║║╔╗║ ║║ ║║║║║╔╗║
# ║║ ║║║║║╔╬╬╗║║║║═╣  ╠══║    ║║ ║║║╚═╝║║╚╝║║║ ╚═══╝╔╣╠╗║╚╝║║║║║║║╠══║    ║╚═╝║║║═╣ ║╚╗║╚╝║║╚╝║
# ╚╝ ╚═╝╚╝╚╝╚╝╚╝╚══╝  ╚══╝    ╚╝ ╚╝╚═╗╔╝║╔═╝╚╝      ╚══╝╚═╗║╚╝╚╝╚╝╚══╝    ╚═══╝╚══╝ ╚═╝╚══╝║╔═╝
#                                  ╔═╝║ ║║              ╔═╝║                               ║║
#                                  ╚══╝ ╚╝              ╚══╝                               ╚╝
#
from typing import Callable

from ignis import widgets
from .entry import SettingEntry


class SliderEntry(SettingEntry):

    def __init__(self, text_context: str, on_change: function | Callable, s_min: float, s_max: float, step: float, default_state: float=0):
        self._text_context = widgets.Label(
            css_classes=["pagetext"],
            justify="left",
            wrap=False,
            wrap_mode='word',
            label=text_context
        )
        self._slider = widgets.Scale(
            css_classes=["slider"],
            vertical=False,
            min=s_min,
            max=s_max,
            step=step,
            value=default_state if s_min <= default_state <= s_max else s_min,
            on_change=on_change,
            draw_value=True,
            value_pos="left"
        )

        super().__init__(
            widgets.CenterBox(
                hexpand=True,
                vexpand=True,
                start_widget=widgets.Box(child=[self._text_context]),
                center_widget=widgets.Box(),
                end_widget=widgets.Box(child=[self._slider])
            )
        )
