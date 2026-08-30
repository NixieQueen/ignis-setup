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
    PictureEntry, InfoEntry, SubHeaderEntry
)
from ignis.services.fetch import FetchService
import math


fetch = FetchService.get_default()


class AboutPage(SettingsNavigation):

    def __init__(self, active_screen):
        self.pages = []
        self.active_screen = active_screen

        self._logo = PictureEntry(fetch.os_logo)
        self._os_name = InfoEntry("Operating system:", fetch.os_name)
        self._session_type = InfoEntry("Session:", fetch.session_type)
        self._current_desktop = InfoEntry("Desktop environment:", fetch.current_desktop)
        self._hostname = InfoEntry("Hostname:", fetch.hostname.rstrip('\n'))
        self._kernel = InfoEntry("Kernel:", fetch.kernel)

        self._cpu_header = SubHeaderEntry("Hardware")

        self._cpu = InfoEntry("CPU:", fetch.cpu)
        self._memory = InfoEntry("Memory:", f"{math.ceil(fetch.mem_info['MemTotal']/1000000)}GB")
        self._mb = InfoEntry("Motherboard:", fetch.board_vendor)
        self._bios = InfoEntry("Bios version:", fetch.board_name)

        self._gtk_header = SubHeaderEntry("GTK")

        self._gtk_theme = InfoEntry("GTK theme:", fetch.gtk_theme)
        self._icon_theme = InfoEntry("Icon theme:", fetch.icon_theme)
        
        self._page = SettingsPage(
            name='About',
            children=[
                self._logo,
                self._os_name,
                self._session_type,
                self._current_desktop,
                self._hostname,
                self._kernel,
                self._cpu_header,
                self._cpu,
                self._memory,
                self._mb,
                self._bios,
                self._gtk_header,
                self._gtk_theme,
                self._icon_theme
            ]
        )

        super().__init__(
            icon_image="user-home-symbolic",
            onclick=lambda _: self.clicked(),
            tooltip_text="About"
        )

    def clicked(self):
        for page in self.pages:
            page.deactivate()

        self.activate()
        self.active_screen.set_value(self._page)
        
