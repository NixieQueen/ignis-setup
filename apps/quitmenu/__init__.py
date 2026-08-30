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
from services import ConfigService
from .quitmenu_widgets import Clock


config = ConfigService.get_default()
windowmanager = WindowManager.get_default()
commandmanager = CommandManager.get_default()
        

class quitmenu_creator(widgets.RevealerWindow):

    def __init__(self):        
        self.clock = Clock(config.get_value('quitmenu_timer'))
        
        self.revealer_widget = widgets.Revealer(
            #transition_type="swing_up",
            transition_type="crossfade",
            #transition_type="crossfade",
            transition_duration=1000,
            reveal_child=True,
            child=self.clock
        )

        super().__init__(
            namespace=f"ignis_quitmenu",
            visible=False,
            monitor=1,
            anchor=["top", "left", "bottom", "right"],
            exclusivity="ignore",  # Ignore may be needed but could overlap with taskbar
            layer="overlay",
            kb_mode="exclusive",
            popup=True,
            css_classes=["unset"],
            setup=lambda self: self.connect(
                "notify::visible", lambda x, _: self.open_quitmenu()  # Can cause a loop if 'self.visible == False' is not properly ignored
            ),
            revealer=self.revealer_widget,
            child=widgets.Box(
                valign="baseline_center",
                halign="baseline_center",
                #vertical=True,
                child=[
                    self.revealer_widget
                ],
            )
        )

    def open_quitmenu(self):
        if self.visible:
            self.clock.start_timer()
        else:
            self.clock.end_timer()
        
    def close_quitmenu(self):
        windowmanager.close_window(f"ignis_quitmenu")

    @commandmanager.command(name="launch-quitmenu")
    def launch_quitmenu(*_):    
        windowmanager.open_window(f"ignis_quitmenu")
