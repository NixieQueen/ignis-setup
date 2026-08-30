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
from extra_widgets import TaskbarHover
from services import ConfigService


config = ConfigService.get_default()


def get_taskbar_content(monitor_id: int=0) -> Widget.Window:
    app_child = Apps(monitor_id=monitor_id)
    match config.get_value('taskbar_position'):
        case 'standard':
            if config.get_value('taskbar_anchor') == "linux": 
                return Widget.Window(
                    namespace=f"ignis_taskbar_panel_{monitor_id}",
                    monitor=monitor_id,
                    anchor=["left", "bottom", "right"],
                    exclusivity="exclusive",
                    #layer = "overlay",
                    child=Widget.CenterBox(
                        css_classes=["taskbar"],
                        style="border-radius: 0rem; margin: 0rem;",
                        start_widget=Widget.Box(),
                        center_widget=Widget.Box(child=[app_child]),
                        end_widget=Widget.Box(),
                    )
                )
            else:
                return Widget.Window(
                    namespace=f"ignis_taskbar_panel_{monitor_id}",
                    monitor=monitor_id,
                    anchor=["left", "bottom", "right"],
                    exclusivity="exclusive",
                    #layer = "overlay",
                    child=Widget.CenterBox(
                        css_classes=["taskbar"],
                        style="border-radius: 0rem; margin: 0rem;",
                        start_widget=Widget.Box(child=[app_child]),
                        center_widget=Widget.Box(),
                        end_widget=Widget.Box(),
                    )
                )

        case 'unity':
            return Widget.Window(
                namespace=f"ignis_taskbar_panel_{monitor_id}",
                monitor=monitor_id,
                anchor=["top", "left", "bottom"],
                exclusivity="exclusive",
                #layer = "overlay",
                child=Widget.CenterBox(
                    css_classes=["taskbar"],
                    style="border-radius: 2rem;",
                    start_widget=Widget.Box(child=[app_child]),
                    center_widget=Widget.Box(),
                    end_widget=Widget.Box(),
                )
            )

        case 'floating':
            if config.get_value('taskbar_hiding'):
                return Widget.Window(
                    namespace=f"ignis_taskbar_panel_{monitor_id}",
                    monitor=monitor_id,
                    anchor=["bottom"],
                    exclusivity="normal",
                    child=Widget.CenterBox(
                        start_widget=Widget.Box(),
                        center_widget=TaskbarHover(app_child),
                        end_widget=Widget.Box(),
                    )
                )
            else:
                return Widget.Window(
                    namespace=f"ignis_taskbar_panel_{monitor_id}",
                    monitor=monitor_id,
                    anchor=["bottom"],
                    exclusivity="normal",
                    child=Widget.CenterBox(
                        css_classes=["taskbar"],
                        style="border-radius: 2rem 2rem 0rem 0rem; margin: 0rem;",
                        start_widget=Widget.Box(),
                        center_widget=Widget.Box(child=[app_child]),
                        end_widget=Widget.Box(),
                    )
                )

        case _:
            return Widget.Window(
                namespace=f"ignis_taskbar_panel_broken_{monitor_id}"
            )
