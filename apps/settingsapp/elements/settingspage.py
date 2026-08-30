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
from extra_widgets import TextButton


class SettingsPage(widgets.Scroll):

    def __init__(self, name: str, children: list, apply_function: Callable | None=None, save_function: Callable | None=None, spacing: int=0) -> None:
        if apply_function:
            function_box_content = []
            self._apply_button = TextButton('Apply', on_click=apply_function)
            function_box_content.append(widgets.Box(child=[self._apply_button], css_classes=['apply_button']))
            if save_function:
                self._save_button = TextButton('Save', on_click=save_function)
                function_box_content.append(widgets.Box(child=[self._save_button], css_classes=['apply_button']))
            self._apply_box = widgets.CenterBox(
                css_classes=["apply_button_container"],
                vertical=False,
                hexpand=True,
                start_widget=widgets.Box(),
                center_widget=widgets.Box(),
                end_widget=widgets.Box(child=function_box_content)
            )

        self._page_label = widgets.Label(
            label=name, css_classes=["pageheader"], halign="start"
        )


        self._page_content = widgets.Box(
            vertical=True,
            hexpand=True,
            vexpand=True,
            spacing=spacing,
            child=[
                self._page_label,
                *children
            ]    
        )
        
        super().__init__(
            hexpand=True,
            vexpand=True,
            child=widgets.CenterBox(
                vertical=True,
                hexpand=True,
                vexpand=True,
                css_classes=["page"],
                start_widget=self._page_content,
                center_widget = widgets.Box(),
                end_widget = widgets.Box(child=[self._apply_box if apply_function else None])
        
            )
        )

    def update_content(self, children):
        self._page_content.child = [
            self._page_label,
            *children
        ]
    
