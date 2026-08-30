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
from ignis.window_manager import WindowManager
from ignis.command_manager import CommandManager
from ignis import utils as Utils
from services import ScreennameToId

screenname = ScreennameToId.get_default()

from .applauncher_widgets import AppGrid

from ignis.services.niri import NiriService
way_wm = NiriService.get_default()
window_manager = WindowManager.get_default()
commandmanager = CommandManager.get_default()

applaunchers = []


@commandmanager.command(name="launch-applauncher")
def launch_applauncher(monitor="-1", *_):
    if not monitor.lstrip("-").isnumeric():
        return
    monitor = int(monitor)
    
    if monitor < 0:
        monitor = screenname.name_to_id(way_wm.active_output)
        #monitor = way_wm.active_workspace.monitor_id


    if len(applaunchers)-1 < monitor:
        return

    applaunchers[monitor].visible = True


class applauncher(Widget.RevealerWindow):

    def __init__(self, monitor_id: int=0):
        self.monitor_id = monitor_id

        self.appgrid = AppGrid()

        self.revealer_widget = Widget.Revealer(
            #transition_type="swing_up",
            transition_type="slide_up",
            #transition_type="crossfade",
            transition_duration=600,
            reveal_child=True,
            child=Widget.Box(
                vertical=True,
                css_classes=["applauncher"],
                child=[
                    self.appgrid
                ]
            )
        )

        super().__init__(
            namespace=f"ignis_applauncher_{monitor_id}",
            visible=False,
            monitor=monitor_id,
            #anchor=["top", "left", "bottom", "right"],
            anchor=["left", "bottom"],  # This does not allow click to close!
            exclusivity="normal",  # Ignore may be needed but could overlap with taskbar
            layer="overlay",
            kb_mode="exclusive",
            popup=True,
            css_classes=["unset"],
            setup=lambda self: self.connect(
                "notify::visible", lambda x, _: self.applauncher_open()  # Can cause a loop if 'self.visible == False' is not properly ignored
            ),
            revealer=self.revealer_widget,
            child=Widget.Box(
                vertical=True,
                child=[
                    Widget.Button(
                        vexpand=True,
                        hexpand=True,
                        css_classes=["unset"],
                        on_click=lambda x: self.close_applaunchers(-1)
                    ),
                    Widget.Box(
                        child=[
                            self.revealer_widget,
                            Widget.Button(
                                vexpand=True,
                                hexpand=True,
                                css_classes=["unset"],
                                on_click=lambda x: self.close_applaunchers(-1)
                            )
                        ]
                    )
                ]
            )
        )
        applaunchers.append(self)

    def applauncher_open(self):
        if not self.visible:
            return  # This may not properly close the searchbar's focus, no idea how to fix :(

        self.appgrid.searchbar.bar.set_text('')  # Reset searchapp to empty for typing
        self.appgrid.searchbar.bar.grab_focus()  # Turn on the searchapp bar
        self.appgrid.change_page(0)
        self.close_applaunchers(self.monitor_id)

    def close_applaunchers(self, keep_open_index):
        for i in range(Utils.get_n_monitors()):
            if i == keep_open_index:
                continue
            window_manager.close_window(f"ignis_applauncher_{i}")
