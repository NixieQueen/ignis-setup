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
from ignis.widgets import Widget
from ignis.app import IgnisApp
from ignis.services.applications import ApplicationsService, Application
from ignis.menu_model import IgnisMenuModel, IgnisMenuItem, IgnisMenuSeparator
from ignis.utils import Utils
from ignis.services.hyprland import HyprlandService

icon_size = 56

applications = ApplicationsService.get_default()
app = IgnisApp.get_default()
hyprland = HyprlandService.get_default()

TERMINAL_FORMAT = "kitty %command%"

class PinnedAppItem(Widget.Button):
    def __init__(self, app: Application):
        menu = Widget.PopoverMenu(
            model=IgnisMenuModel(
                IgnisMenuItem(label="Launch", on_activate=lambda x: app.launch()),
                IgnisMenuSeparator(),
                *(
                    IgnisMenuItem(
                        label=i.name, on_activate=lambda x, action=i: action.launch()
                    )
                    for i in app.actions
                ),
                IgnisMenuSeparator(),
                IgnisMenuItem(label="Unpin", on_activate=lambda x: app.unpin()),
            )
        )

        super().__init__(
            child=Widget.Box(child=[Widget.Icon(image=app.icon, pixel_size=icon_size), menu]),
            on_click=lambda x: app.launch(terminal_format=TERMINAL_FORMAT),
            on_right_click=lambda x: menu.popup(),
            css_classes=["taskbar_apps", "unset"],
        )

class ActiveAppItem(Widget.Button):
    # This takes in a hyprland window!
    def __init__(self, app):
        if app.hidden:
            return

        menu = Widget.PopoverMenu(
            model=IgnisMenuModel(
                IgnisMenuItem(label="Launch", on_activate=lambda x: hyprland.send_command(f"dispatch exec {app.class_name.lower()}")),
                IgnisMenuItem(label="Pin", on_activate=lambda x: app.pin()),
            )
        )

        super().__init__(
            child=Widget.Box(child=[Widget.Icon(image=Utils.get_app_icon_name(app.class_name), pixel_size=icon_size), menu]),
            on_click=lambda x: hyprland.send_command(f"dispatch focuswindow pid:{app.pid}"),
            on_right_click=lambda x: menu.popup(),
            css_classes=["taskbar_apps", "unset"],
        )



class PinnedApps(Widget.Box):
    def __init__(self):
        super().__init__(
            child=applications.bind(
                "pinned",
                transform=lambda value: [PinnedAppItem(app) for app in value]
                + [
                    Widget.Button(
                        child=Widget.Icon(image="start-here-symbolic", pixel_size=icon_size),
                        on_click=lambda x: app.toggle_window("ignis_LAUNCHER"),
                        css_classes=["taskbar_apps", "unset"],
                    )
                ],
            )
        )

class ActiveApps(Widget.Box):
    def __init__(self):
        super().__init__(
            child=hyprland.bind(
                "windows",
                transform=lambda value: [ActiveAppItem(app) for app in value]
            )
        )


class Apps (Widget.CenterBox):
    def __init__(self):
        super().__init__(
            start_widget = PinnedApps(),
            center_widget = ActiveApps(),
            end_widget = Widget.Box(),
        )
