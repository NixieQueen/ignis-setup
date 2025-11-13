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
from ignis.services.niri import NiriService
from ignis.services.fetch import FetchService
from ignis.command_manager import CommandManager
from ignis import utils as Utils


fetch = FetchService.get_default()
niri = NiriService.get_default()
way_wm = niri
systemd_session = SystemdService.get_default()
commandmanager = CommandManager.get_default()
gamemode_buttons = []


@commandmanager.command(name="toggle-gamemode")
def toggle_gamemode(*_) -> None:
    gamemode_buttons[0].gaming_button.toggle_gamemode()


class hyprIdleButton(ServiceHover):

    def __init__(self):
        self.hypridle_unit = systemd_session.get_unit('hypridle.service')
        self.label = Widget.Label(
            label = self.hypridle_unit.bind('is_active', lambda x: 'Ready to sleep...' if x else "I'm awake!"),
            css_classes = ['toppanel_font']
        )
     
        super().__init__(
            icon_image='gnome-disks-state-standby-symbolic',
            info_child=self.label,
            on_click=lambda _: self.toggle_hypridle()
        )
        self.service_button.css_classes = self.hypridle_unit.bind(
            'is_active',
            lambda x:
                ['toppanel_button'] if x else ['toppanel_button', 'disabled']
        )

    def toggle_hypridle(self):
        if self.hypridle_unit.is_active:
            asyncio.create_task(self.hypridle_unit.stop_async())
            return

        asyncio.create_task(self.hypridle_unit.start_async())
        
        
class niriIdleButton(ServiceHover):

    def __init__(self):
        self.swayidle_unit = systemd_session.get_unit('swayidle.service')
        
        self.label = Widget.Label(
            label = self.swayidle_unit.bind('is_active', lambda x: f'Ready to sleep...' if x else "I'm awake!"),
            css_classes = ['toppanel_font']
        )
     
        super().__init__(
            icon_image='gnome-disks-state-standby-symbolic',
            info_child=self.label,
            on_click=lambda _: self.toggle_hypridle()
        )
        self.service_button.css_classes = self.swayidle_unit.bind(
            'is_active',
            lambda x:
                ['toppanel_button'] if x else ['toppanel_button', 'disabled']
        )

    def toggle_hypridle(self):
        if self.swayidle_unit.is_active:
            asyncio.create_task(self.swayidle_unit.stop_async())
            return

        asyncio.create_task(self.swayidle_unit.start_async())
        
        
class gamingButton(ServiceHover):

    def __init__(self):
        self.gamemode = False

        self.label = Widget.Label(
            label = 'Not gaming 3:',
            css_classes = ['toppanel_font']
        )
        
        super().__init__(
            icon_image='applications-games-symbolic',
            info_child=self.label,
            on_click=lambda _: self.toggle_gamemode()
        )
        self.service_button.css_classes = ['toppanel_button', 'disabled']

    def toggle_gamemode(self):
        self.gamemode = not self.gamemode
        for button in gamemode_buttons:
            gaming_button = button.gaming_button  # Works because it requires itself to be always present
            gaming_button.gamemode = self.gamemode
            gaming_button.service_button.css_classes = ['toppanel_button'] if self.gamemode else ['toppanel_button', 'disabled']
            gaming_button.label.label = "Gaming! :3" if self.gamemode else "Not gaming 3:"

        performance_toggle = 'false' if self.gamemode else 'true'
        asyncio.create_task(Utils.exec_sh_async(
            f"hyprctl --batch 'keyword decoration:blur:enabled {performance_toggle} ; keyword decoration:shadow:enabled {performance_toggle} ; keyword animations:enabled {performance_toggle} ; keyword misc:vfr {performance_toggle}'"
        ))
        

class powerButton(ServiceHover):

    def __init__(self):
        self.label = Widget.Label(
            label = "uptime: ",
            css_classes = ['toppanel_font']
        )
        fetch_poll = Utils.Poll(timeout=60000, callback=lambda _: self.update_uptime())

        super().__init__(
            icon_image='system-shutdown-symbolic',
            info_child=self.label,
            on_click=lambda _: None
        )

    def update_uptime(self):
        fetch_uptime = fetch.uptime or (0, 0, 0, 0)
        self.label.label = f"uptime: {fetch_uptime[0]} days {fetch_uptime[1]}h{fetch_uptime[2]}m{fetch_uptime[3]}s"
        

class Buttons(Widget.Box):

    def __init__(self):
        # Hypridle and Gaming mode are both dependant on hyprland
        # This should be changed to allow Niri to occupy a similar role
        self.gaming_button = gamingButton()  # Pre init to access later
        service_child = [
            niriIdleButton() if niri.is_available else hyprIdleButton(),
            self.gaming_button,
            powerButton()
        ]
        
        super().__init__(
            child=service_child,
            css_classes=['toppanel_workspace']
        )
        gamemode_buttons.append(self)
