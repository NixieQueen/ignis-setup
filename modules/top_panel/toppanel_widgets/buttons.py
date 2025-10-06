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
#
# Creates buttons for services on the top panel
# : Hypridle
# : Gaming mode
# : Power button
#
import asyncio
from .services import ServiceHover
from ignis import widgets as Widget
from ignis.services.systemd import SystemdService
from ignis.services.hyprland import HyprlandService
from ignis import utils as Utils


hyprland = HyprlandService.get_default()
systemd_session = SystemdService.get_default()
hypridle_unit = systemd_session.get_unit('hypridle.service')
gamemode_buttons = []


class hyprIdleButton(ServiceHover):

    def __init__(self):
        super().__init__(
            icon_image='gnome-disks-state-standby-symbolic',
            info_child=Widget.Box(),
            on_click=lambda _: self.toggle_hypridle()
        )
        self.service_button.css_classes = hypridle_unit.bind(
            'is_active',
            lambda x:
                ['toppanel_button'] if x else ['toppanel_button', 'disabled']
        )

    def toggle_hypridle(self):
        if hypridle_unit.is_active:
            asyncio.create_task(hypridle_unit.stop_async())
            return

        asyncio.create_task(hypridle_unit.start_async())
        
        
class gamingButton(ServiceHover):

    def __init__(self):
        self.gamemode = False
        super().__init__(
            icon_image='applications-games-symbolic',
            info_child=Widget.Box(),
            on_click=lambda _: self.toggle_gamemode()
        )
        self.service_button.css_classes = ['toppanel_button', 'disabled']

    def toggle_gamemode(self):
        self.gamemode = not self.gamemode
        for button in gamemode_buttons:
            gaming_button = button.gaming_button  # Works because it requires itself to be always present
            gaming_button.gamemode = self.gamemode
            gaming_button.service_button.css_classes = ['toppanel_button'] if self.gamemode else ['toppanel_button', 'disabled']

        performance_toggle = 'false' if self.gamemode else 'true'
        asyncio.create_task(Utils.exec_sh_async(
            f"hyprctl --batch 'keyword decoration:blur:enabled {performance_toggle} ; keyword decoration:shadow:enabled {performance_toggle} ; keyword animations:enabled {performance_toggle} ; keyword misc:vfr {performance_toggle}'"
        ))
        

class powerButton(ServiceHover):

    def __init__(self):

        super().__init__(
            icon_image='system-shutdown-symbolic',
            info_child=Widget.Box(),
            on_click=lambda _: None
        )
        

class Buttons(Widget.Box):

    def __init__(self):
        # Hypridle and Gaming mode are both dependant on hyprland
        # This should be changed to allow Niri to occupy a similar role
        self.gaming_button = gamingButton()  # Pre init to access later
        service_child = [
            hyprIdleButton() if hyprland else None,
            self.gaming_button,
            powerButton()
        ]
        
        super().__init__(
            child=service_child,
            css_classes=['toppanel_workspace']
        )
        gamemode_buttons.append(self)
