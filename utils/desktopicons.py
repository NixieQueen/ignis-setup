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
from utils.themeicons import get_theme_icon
from utils.desktopfiles import DesktopApps
from utils.desktopfiles import get_icon_path
from ignis import utils as Utils
from ignis import widgets as Widget

from ignis.services.hyprland import HyprlandService
hyprland = HyprlandService.get_default()

# class containing basic data for an app icon
class App:
    def __init__(self, class_name: str, theme: None=None, exec_cmd: str="", pinned_apps: None=None, addresses: list=[], desktopfiles: DesktopApps | None=None, icon_path: str="", icon_size: int=50):
        self.class_name = class_name
        self.exec_cmd = exec_cmd if exec_cmd else class_name.lower()
        self.pinned_apps = pinned_apps
        self.addresses = addresses
        self.address_index = 0
        self.icon_size = icon_size
        self.theme = theme if theme else 'nixie'

        if not icon_path:
            icon_path = get_theme_icon(class_name, self.theme)

            if not icon_path:
                icon_path = Utils.get_app_icon_name(class_name)

                if not icon_path and desktopfiles:
                    desktopfile_names = [desktopfile.name.lower() for desktopfile in desktopfiles.desktop_files.value]
                    print(class_name)
                    print(desktopfile_names)
                    if class_name.lower() in desktopfile_names:
                        icon_path = desktopfiles.desktop_files.value[desktopfile_names.index(class_name.lower())].icon_path

                    if not icon_path:  # This might be excessively expensive, reevaluate
                        xdg_data_dirs = list(desktopfiles.xdg_data_dirs.keys())
                        icon_path = get_icon_path(class_name.lower(), self.theme, xdg_data_dirs[0], xdg_data_dirs)

        self.icon_path = icon_path
        self.icon = Widget.Icon(image=icon_path, pixel_size=icon_size)

    def launch(self):
        hyprland.send_command(f"dispatch exec {self.exec_cmd}")

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
        if not self.pinned_apps:
            return

        self.pinned_apps.add_pinned_app(self.class_name, self.icon_path)

    def unpin(self):
        if not self.pinned_apps:
            return

        self.pinned_apps.remove_pinned_app(self.class_name)
