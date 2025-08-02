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
from utils.ignisconfig import Config

from .taskbar_widgets import Apps

def taskbar_layout_creator(config):
    if config.config['taskbar'] == "unity":
        return Widget.CenterBox(
            css_classes=["taskbar"],
            start_widget=Widget.Box(child=[Apps(config)]),
            center_widget=Widget.Box(),
            end_widget=Widget.Box()
        )
    else:
        return Widget.CenterBox(
            css_classes=["taskbar"],
            start_widget=Widget.Box(),
            center_widget=Widget.Box(child=[Apps(config)]),
            end_widget=Widget.Box(),
        )


def taskbar_anchor_creator(config):
    match config.config['taskbar']:
        case "unity":
            return ["bottom", "left", "top"]

        case "floating":
            return ["bottom"]

        case _:
            return ["left", "bottom", "right"]



def taskbar_creator(config: Config, monitor_id: int=0) -> Widget.Window:
    return Widget.Window(
        namespace=f"ignis_taskbar_panel_{monitor_id}",
        monitor=monitor_id,
        anchor=taskbar_anchor_creator(config),
        exclusivity="exclusive" if not config.config['taskbar'] == "floating" else "normal",
        #layer = "overlay",
        child=taskbar_layout_creator(config),
    )
