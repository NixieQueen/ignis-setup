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
from ignis.window_manager import WindowManager
from ignis.services.hyprland import HyprlandService
from utils.desktopicons import App

hyprland = HyprlandService.get_default()
window_manager = WindowManager.get_default()

class PinnedAppsHandler:

    class PinnedApp:

        def __init__(self, class_name, icon_path):
            self.class_name = class_name
            self.icon_path = icon_path

    def __init__(self):
        self.path = Utils.get_current_dir()
        self.pinned_apps = []
        try:
            self.load_pinned_apps()
        except FileNotFoundError:
            pass

    def load_pinned_apps(self):
        self.pinned_apps = []
        with open(f"{self.path}/pinned_apps") as pinned_app_file:
            for line in pinned_app_file:
                line = line.rstrip('\n')
                line = line.split(": ")
                self.pinned_apps.append(self.PinnedApp(line[0], line[1]))

    def append_pinned_apps(self, pinned_app=None):
        with open(f"{self.path}/pinned_apps","a") as pinned_app_file:
            if pinned_app:
                pinned_app_file.write(f"{pinned_app.class_name}: {pinned_app.icon_path}\n")

            else:
                for pinned_app in self.pinned_apps:
                    pinned_app_file.write(f"{pinned_app.class_name}: {pinned_app.icon_path}\n")

    def save_pinned_apps(self):
        with open(f"{self.path}/pinned_apps","w") as pinned_app_file:
            pinned_app_file.write("")

        self.append_pinned_apps()

    def add_pinned_app(self, class_name, icon_path):
        if class_name in [pinned_app.class_name for pinned_app in self.pinned_apps]:
            return

        new_pinned_app = self.PinnedApp(class_name, icon_path)
        self.pinned_apps.append(new_pinned_app)
        self.append_pinned_apps(new_pinned_app)

    def remove_pinned_app(self, class_name):
        pinned_app_classnames = [pinned_app.class_name for pinned_app in self.pinned_apps]
        if not class_name in pinned_app_classnames:
            return

        self.pinned_apps.pop(pinned_app_classnames.index(class_name))
        self.save_pinned_apps()


class ActiveAppBox(Widget.Box):

    def __init__(self, current_address: str, app_address: str, address_size: int):
        padding_width = 1.8 / float(address_size) - 0.05 * (float(address_size) - 1)
        if padding_width < 0.2:
            padding_width = 0.2
        super().__init__(
            css_classes=["taskbar_apps_separators", "unset"],
            halign="start",
            valign="center",
            style=f"padding: 0.3rem {padding_width}rem;"
        )
        if current_address == app_address:
            self.add_css_class('active')


class AppButton(Widget.Button):
    def __init__(self, app: App, menu: Widget.PopoverMenu=None, is_pinned: bool=False):
        if not menu:
            menu = Widget.PopoverMenu(
                model=IgnisMenuModel(
                    IgnisMenuItem(label="Launch", on_activate=lambda _: app.launch()),
                    IgnisMenuItem(label="Pin", on_activate=lambda _: app.pin()),
                )
            )

        if app.addresses:
            separator_box = Widget.CenterBox(
                center_widget=Widget.Box(
                    child=hyprland.bind(
                        "active_window",
                        transform=lambda client: [
                            ActiveAppBox(client.address, address, len(app.addresses)) for address in app.addresses
                        ],
                    )
                )
            )
            icon_box = Widget.Box(child=[app.icon, separator_box], vertical=True)
        else:
            icon_box = app.icon

        if not is_pinned:
            super().__init__(
                child=Widget.Box(child=[icon_box, menu]),
                on_click=lambda _: app.focus(),
                on_right_click=lambda _: menu.popup(),
                css_classes=["taskbar_apps", "unset"],
            )
        else:
            super().__init__(
                child=Widget.Box(child=[icon_box, menu]),
                on_click=lambda _: app.launch(),
                on_right_click=lambda _: menu.popup(),
                css_classes=["taskbar_apps", "pinned"],
            )


class PinnedAppButton(AppButton):

    def __init__(self, app: App):
        menu = Widget.PopoverMenu(
            model=IgnisMenuModel(
                IgnisMenuItem(label="Launch", on_activate=lambda _: app.launch()),
                IgnisMenuItem(label="Unpin", on_activate=lambda _: app.unpin()),
            )
        )
        super().__init__(app, menu, is_pinned=True)


class AppLauncher(Widget.Button):
    def __init__(self, monitor_id):
        super().__init__(
            child=Widget.Icon(image="start-here-symbolic", pixel_size=50),
            on_click=lambda x: window_manager.open_window(f"ignis_applauncher_{monitor_id}"),
            css_classes=["taskbar_apps", "pinned"]
        )


class PinnedApps(Widget.Box):
    def __init__(self, pinned_apps, config):
        self.config = config
        self.pinned_apps = pinned_apps
        super().__init__(
            vertical = True if config.config['taskbar_position'] == 'unity' else False,
            child=hyprland.bind(
                "windows",
                transform=lambda windows: self.generate_pinnedapp_list(windows)
            )
        )

    def generate_pinnedapp_list(self, windows):
        hyprland_window_classnames = [window.class_name for window in windows]
        return [
            PinnedAppButton(
                App(
                    class_name=pinned_app.class_name,
                    theme=self.config.config['theme'],
                    pinned_apps=self.pinned_apps,
                    icon_path=pinned_app.icon_path
                )
            ) for pinned_app in self.pinned_apps.pinned_apps if pinned_app.class_name not in hyprland_window_classnames
        ]


class ActiveApps(Widget.Box):
    def __init__(self, pinned_apps, config, desktopfiles):
        self.config = config
        self.desktopfiles = desktopfiles
        self.pinned_apps = pinned_apps
        super().__init__(
            vertical = True if config.config['taskbar_position'] == 'unity' else False,
            child=hyprland.bind(
                "windows",
                transform=lambda windows: self.generate_app_list(windows)
            )
        )

    def generate_app_list(self, windows):
        active_windows = self.sort_windows(windows)
        return [
            AppButton(
                App(
                    class_name=w_class,
                    theme=self.config.config['theme'],
                    pinned_apps=self.pinned_apps,
                    addresses=active_windows[w_class],
                    desktopfiles=self.desktopfiles
                )
            ) for w_class in active_windows
        ]

    def sort_windows(self, windows):
        # Make this function return a dictionary of all active apps sorted by class_name
        active_windows = {}
        for w in windows:
            class_name = w.class_name or w.title

            if not class_name in active_windows:
                active_windows[class_name] = []

            active_windows[class_name].append(w.address)

        return active_windows


pinned_apps = PinnedAppsHandler()


class Apps (Widget.Box):
    def __init__(self, config, desktopfiles, monitor_id):
        super().__init__(
            vertical = True if config.config['taskbar_position'] == 'unity' else False,
            child=[
                AppLauncher(monitor_id),              # The launcher button, as just one button
                PinnedApps(pinned_apps, config),   # A list, precompiled from some txt file, of all pinned apps
                ActiveApps(pinned_apps, config, desktopfiles),      # All apps that are open right now
            ]
        )
