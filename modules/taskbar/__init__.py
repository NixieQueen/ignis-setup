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

from .taskbar_widgets import Apps

def get_anchor(config):
    match config.config['taskbar_position']:
        case 'standard':
            return ["left", "bottom", "right"]

        case 'unity':
            return ["top", "left", "bottom"]

        case 'floating':
            return ["bottom"]


def taskbar_creator(config, monitor_id: int=0) -> Widget.Window:
    return Widget.Window(
        namespace=f"ignis_taskbar_panel_{monitor_id}",
        monitor=monitor_id,
        anchor=get_anchor(config),
        exclusivity="normal" if config.config['taskbar_position'] == 'floating' else "exclusive",
        #layer = "overlay",
        child=Widget.CenterBox(
            css_classes=["taskbar"],
            start_widget=Widget.Box(),
            center_widget=Widget.Box(child=[Apps(config=config)]),
            end_widget=Widget.Box(),
        ) if (config.config['taskbar_anchor'] == 'linux' and (not config.config['taskbar_position'] == 'unity')) else
        Widget.CenterBox(
            css_classes=["taskbar_unity"],
            start_widget=Widget.Box(child=[Apps(config=config)]),
            center_widget=Widget.Box(),
            end_widget=Widget.Box(),
        ),
    )
