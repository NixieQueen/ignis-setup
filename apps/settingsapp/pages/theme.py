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
    PictureEntry, SubHeaderEntry,
    InfoEntry, DropdownEntry,
    SwitchEntry
    
)
from ignis.app import IgnisApp
from services import ConfigService, NiriConfigService

from ignis.services.fetch import FetchService


app = IgnisApp.get_initialized()
fetch = FetchService.get_default()
config = ConfigService.get_default()
niriconfig = NiriConfigService.get_default()


class ThemePage(SettingsNavigation):

    def __init__(self, active_screen, path: str):
        self.pages = []
        self.active_screen = active_screen

        self._themes = ["nixie", "beachy", "snowy", "cutesy"]

        self._title = SubHeaderEntry("Choose your theme!")
        self._theme_chooser = DropdownEntry("Theme", lambda _, x: config.set_value("theme", x), self._themes, config.get_value('theme'))

        self._theme_entries = list()
        for theme in self._themes:
            self._theme_entries.append(
                InfoEntry('Theme name', theme)
            )
            self._theme_entries.append(
                PictureEntry(f'{path}/themes/{theme}/themepreview.png', width=384, height=216)
            )

        self._blur_button = SwitchEntry("Enable blur on Ignis", lambda x: niriconfig.assign_config_value('blur', x.clicked), niriconfig.get_value('blur'))
                
        self._page = SettingsPage(
            name='Theming',
            apply_function=lambda _: self.apply_function(),
            save_function=lambda _: self.save_function(),
            spacing=5,
            children=[
                self._title,
                self._theme_chooser
            ]
            + self._theme_entries +
            [
                self._blur_button
            ]
        )
        
        super().__init__(
            icon_image="applications-graphics-symbolic",
            onclick=lambda _: self.clicked(),
            tooltip_text="Change your theme!"
        )

    def apply_function(self):
        self.save_function()
        niriconfig.merge()
        app.reload()
        
    def save_function(self):
        config.write_config()
        niriconfig.write_blur_config()

    def clicked(self) -> None:
        for page in self.pages:
            page.deactivate()

        self.activate()
        self.active_screen.set_value(self._page)
        
