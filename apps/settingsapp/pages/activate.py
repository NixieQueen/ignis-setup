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
from ..elements import (
    SettingsNavigation, SettingsPage,
    PictureEntry, InfoEntry, SubHeaderEntry,
    ButtonEntry
)
from ignis import utils
import asyncio
from ignis.services.fetch import FetchService
from services import ConfigService


config = ConfigService.get_default()
fetch = FetchService.get_default()


class ActivatePage(SettingsNavigation):

    def __init__(self, active_screen):
        self.pages = []
        self.active_screen = active_screen

        self._logo = PictureEntry(fetch.os_logo)
        self._activation_header = SubHeaderEntry("Your Linux activation")
        self._activation_status = InfoEntry("Status of activation: ", "Activated" if config.get_value('activation') else "Not activated!")
        self._activate_button = ButtonEntry("Activate Linux (Payment of $30000)", lambda _: self.activate_button())

        if not config.get_value('activation'):
            self.launch_activate_linux()
        else:
            self._activate_button._button.add_css_class('disabled')
        
        self._page = SettingsPage(
            name='Activation',
            children=[
                self._logo,
                self._activation_header,
                self._activation_status,
                self._activate_button
            ]
        )
        
        super().__init__(
            icon_image="emblem-ok-symbolic",
            onclick=lambda _: self.clicked(),
            tooltip_text="Activate Linux"
        )

    def kill_activate_linux(self) -> None:
        asyncio.create_task(utils.exec_sh_async("kill -9 $(pidof activate-linux)"))

    def launch_activate_linux(self) -> None:
        self.kill_activate_linux()
        asyncio.create_task(utils.exec_sh_async("sleep 1; activate-linux"))

    def activate_button(self) -> None:
        self.kill_activate_linux()
        config.set_value('activation', True)
        self._activate_button._button.add_css_class('disabled')
        self._activation_status._text_info.label = "Activated"

        config.write_config()

    def clicked(self) -> None:
        for page in self.pages:
            page.deactivate()

        self.activate()
        self.active_screen.set_value(self._page)
        
