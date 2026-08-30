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
from ignis import widgets as Widget
from ignis.command_manager import CommandManager
from ignis import utils as Utils
from services import ScreennameToId
from ignis.services.niri import NiriService
from ignis.window_manager import WindowManager
from .sidepanel_widgets import profileBanner, trayGrid, SysButtons, PerformanceSwitch, MusicPlayer


window_manager = WindowManager.get_default()
way_wm = NiriService.get_default()
screenname = ScreennameToId.get_default()
commandmanager = CommandManager.get_default()

sidepanels = []


@commandmanager.command(name="launch-sidepanel")
def launch_sidepanel(monitor="-1", *_):
    if not monitor.lstrip("-").isnumeric():
        return
    monitor = int(monitor)
    
    if monitor < 0:
        monitor = screenname.name_to_id(way_wm.active_output)
        #monitor = way_wm.active_workspace.monitor_id


    if len(sidepanels)-1 < monitor:
        return

    sidepanels[monitor].visible = True


class side_panel_creator(Widget.RevealerWindow):

    def __init__(self, monitor_id: int=0):
        self.scroll_box = Widget.Scroll(
            css_classes=["sidepanel", "scroll"],
            vexpand=True,
            hexpand=True,
            child=Widget.Box(
                vertical=True,
                child=[
                    profileBanner(),
                    Widget.Box(homogeneous=False, child=[trayGrid(), SysButtons()]),
                    PerformanceSwitch(),
                    MusicPlayer()
                ]
            )
        )
        
        self.monitor_id = monitor_id

        self.revealer_widget = Widget.Revealer(
            #transition_type="swing_up",
            transition_type="slide_right",
            #transition_type="crossfade",
            transition_duration=600,
            reveal_child=True,
            child=Widget.Box(
                css_classes=["sidepanel"],
                vertical=True,
                child=[self.scroll_box]
            )
        )

        super().__init__(
            namespace=f"ignis_sidepanel_{monitor_id}",
            visible=False,
            monitor=monitor_id,
            #anchor=["top", "left", "bottom", "right"],
            anchor=["left", "top", "bottom"],  # Loses click to close but works better with blur
            exclusivity="normal",  # Ignore may be needed but could overlap with taskbar
            layer="top",
            kb_mode="exclusive",
            popup=True,
            css_classes=["unset"],
            setup=lambda self: self.connect(
                "notify::visible", lambda x, _: self.sidepanel_open()  # Can cause a loop if 'self.visible == False' is not properly ignored
            ),
            revealer=self.revealer_widget,
            child=Widget.Box(
                #vertical=True,
                child=[
                    self.revealer_widget,
                    Widget.Button(
                        vexpand=True,
                        hexpand=True,
                        css_classes=["unset"],
                        on_click=lambda x: self.close_sidepanels(-1)
                    ),
                ]
            )
        )
        
        sidepanels.append(self)

    def sidepanel_open(self):
        if not self.visible:
            return
        self.close_sidepanels(self.monitor_id)
        

    def close_sidepanels(self, keep_open_index):
        for i in range(Utils.get_n_monitors()):
            if i == keep_open_index:
                continue
            window_manager.close_window(f"ignis_sidepanel_{i}")

