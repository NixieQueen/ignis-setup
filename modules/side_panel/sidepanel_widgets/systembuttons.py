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
import asyncio
import extra_widgets
from ignis import utils, widgets
from ignis.services.systemd import SystemdService
from ignis.window_manager import WindowManager


window_manager = WindowManager.get_default()
systemd_session = SystemdService.get_default()


class SysButtons(widgets.CenterBox):

    def __init__(self):
        pixel_size=50
        css_classes=["sidepanel","sysbuttons","sysbutton"]
        self.shutdown_button = extra_widgets.IconButton(
            icon='system-shutdown-symbolic',
            on_click=lambda _: window_manager.open_window('ignis_quitmenu'),
            css_classes=css_classes,
            pixel_size=pixel_size
        )
        self.gammastep_button = extra_widgets.SysServiceButton(
            service='gammastep.service',
            icon='display-brightness-symbolic',
            css_classes=css_classes,
            pixel_size=pixel_size
        )
        self.idle_button = extra_widgets.SysServiceButton(
            service='swayidle.service',
            icon='gnome-disks-state-standby-symbolic',
            css_classes=css_classes,
            pixel_size=pixel_size
        )
        
        super().__init__(
            vertical=True,
            css_classes=["sidepanel", "sysbuttons", "background"],
            start_widget=widgets.Box(),
            center_widget=widgets.Box(
                child=[self.gammastep_button, self.idle_button, self.shutdown_button],
                homogeneous=True,
                spacing=5
            ),
            end_widget=widgets.Box()
        )
