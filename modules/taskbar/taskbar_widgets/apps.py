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
from ignis.menu_model import IgnisMenuModel, IgnisMenuItem
from ignis import utils as Utils
from ignis.services.hyprland import HyprlandService
from utils.themeicons import get_theme_icon

hyprland = HyprlandService.get_default()


class ActiveAppBox(Widget.Box):

    def __init__(self, current_address: str, app_address: str):
        super().__init__(
            css_classes=["taskbar_apps_separators", "unset"],
            halign="start",
            valign="center",
        )
        if current_address == app_address:
            self.add_css_class('active')


class App:
    def __init__(self, class_name: str, addresses: list=[], icon: Widget.Icon=None, icon_size: int=56, terminal_format: str="kitty %command%"):
        self.class_name = class_name
        self.addresses = addresses
        self.icon = icon
        self.icon_size = icon_size              # Probably not needed?
        self.terminal_format = terminal_format  # Probably not needed?
        self.pinned = False
        self.hidden = False
        self.address_index = 0

        if not self.icon:
            icon_path = get_theme_icon(class_name)

            if not icon_path:
                icon_path = Utils.get_app_icon_name(class_name)

            self.icon = Widget.Icon(image=icon_path, pixel_size=icon_size)

    def launch(self):
        hyprland.send_command(f"dispatch exec {self.class_name.lower()}")

    def focus(self):
        if not self.addresses:
            return

        self.address_index = 0
        if hyprland.active_window.address in self.addresses:
            self.address_index = self.addresses.index(hyprland.active_window.address)
            self.address_index = (self.address_index + 1) % len(self.addresses)  # Looping focus

        hyprland.send_command(f"dispatch focuswindow address:{self.addresses[self.address_index]}")

    def close(self):
        hyprland.send_command(f"dispatch closewindow address:{self.addresses[self.address_index]}")

    def pin(self):
        return


class AppButton(Widget.Button):
    def __init__(self, app: App):
        if app.hidden:
            return

        menu = Widget.PopoverMenu(
            model=IgnisMenuModel(
                IgnisMenuItem(label="Launch", on_activate=lambda x: app.launch()),
                IgnisMenuItem(label="Pin", on_activate=lambda x: app.pin()),
            )
        )

        separator_box = Widget.CenterBox(
            center_widget=Widget.Box(
                spacing = 5,
                child=hyprland.bind_many(
                    ["windows", "active_window"],
                    transform=lambda x, client: [
                        ActiveAppBox(client.address, address) for address in app.addresses
                    ],
                )
            )
        )
        icon_box = Widget.Box(child=[app.icon, separator_box], vertical=True)

        super().__init__(
            child=Widget.Box(child=[icon_box, menu]),
            on_click=lambda x: app.focus(),
            on_right_click=lambda x: menu.popup(),
            css_classes=["taskbar_apps", "unset"],
        )


class AppLauncher(Widget.Box):
    def __init__(self):
        super().__init__()


class PinnedApps(Widget.Box):
    def __init__(self):
        super().__init__()


class ActiveApps(Widget.Box):
    def __init__(self):
        super().__init__(
            child=hyprland.bind(
                "windows",
                transform=lambda windows: self.generate_app_list(windows)
            )
        )

    def generate_app_list(self, windows):
        active_windows = self.sort_windows(windows)
        return [AppButton(App(w_class, active_windows[w_class])) for w_class in active_windows]

    def sort_windows(self, windows):
        # Make this function return a dictionary of all active apps sorted by class_name
        active_windows = {}
        for w in windows:
            if not w.class_name in active_windows:
                active_windows[w.class_name] = []

            active_windows[w.class_name].append(w.address)

        return active_windows


# Figure out how to first get a big list of all active apps, then sort them and finally make the appitem thing


class Apps (Widget.CenterBox):
    def __init__(self):
        super().__init__(
            start_widget = AppLauncher(),   # The launcher button, as just one button
            center_widget = PinnedApps(),   # A list, precompiled from some txt file, of all pinned apps
            end_widget = ActiveApps(),      # All apps that are open right now
        )
