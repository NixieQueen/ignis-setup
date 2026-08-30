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
from ignis import widgets
from ignis.command_manager import CommandManager
from ignis.window_manager import WindowManager
from ignis.variable import Variable

from .pages import (
    AboutPage,
    ActivatePage,
    MonitorPage,
    ThemePage
)


windowmanager = WindowManager.get_default()
commandmanager = CommandManager.get_default()


class settings_creator(widgets.RegularWindow):

    def __init__(self, path: str) -> None:
        self._active_screen = Variable()

        self._about_page = AboutPage(self._active_screen)
        self._monitor_page = MonitorPage(self._active_screen)
        self._theme_page = ThemePage(self._active_screen, path=path)
        self._activation_page = ActivatePage(self._active_screen)

        self._about_page.clicked()

        self._pages = [
            self._about_page,
            self._monitor_page,
            self._theme_page,
            self._activation_page
        ]
        for page in self._pages:
            page.pages = self._pages
                
        self._content = widgets.Box(
            css_classes=["content"],
            hexpand=True,
            vexpand=True,
            child=self._active_screen.bind('value', transform=lambda value: [value])
        )

        self._navigator = widgets.Box(
            css_classes=["navigator"],
            hexpand=False,
            vexpand=True,
            vertical=True,
            child=self._pages
        )

        super().__init__(
            css_classes=["settingsmenu"],
            title='Settings',
            icon_name='embled-system-symbolic',
            default_width=900,
            default_height=600,
            resizable=False,
            hide_on_close=True,
            visible=False,
            titlebar=widgets.HeaderBar(css_classes=['topbar'], show_title_buttons=True),
            child=widgets.Box(hexpand=True, vexpand=True, child=[self._navigator, self._content]),
            namespace="ignis_settingsmenu"
        )

        self.connect("notify::visible", self.__on_open)

    def __on_open(self, *_) -> None:
        if not self.visible:
            return

        '''
        Add any updating content here, like a refresh of options for example!
        '''

        if self._active_screen.value != self._about_page._page:
            self._about_page.clicked()

    @commandmanager.command(name="launch-settings")
    def launch_settings(*_) -> None:
        windowmanager.open_window('ignis_settingsmenu')

    def close_settings(self) -> None:
        self.visible=False
