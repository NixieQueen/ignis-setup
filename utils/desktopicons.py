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
#
# A script for finding all applications' desktop files,
# crafting a list with precompiled data (name, icon location, etc),
# and also setting up an icon
#
from ignis import utils as Utils
import os
from .themeicons import get_theme_icon


# Grab xdg_data_dirs and take only the applications
def get_xdg_data_dirs():
    # This is run once on startup to avoid having to wait on a shell command each time
    xdg_data_dirs = dict()
    for data_dir in Utils.exec_sh("echo $XDG_DATA_DIRS").stdout.split(":"):
        data_dir = data_dir.rstrip('\n')
        applications = []
        for path, dirs, files in os.walk(data_dir+"/applications"):
            applications = [app for app in files if app.split(".")[-1] == "desktop"]
            break
        if not applications:
            continue

        xdg_data_dirs[data_dir] = applications
    return xdg_data_dirs


class DesktopFile:

    def __init__(self, name: str, exec_cmd: str, path: str, icon_path: str):
        self.name = name
        self.exec_cmd = exec_cmd
        self.path = path

        # icon_path can either be a path, or more likely, a name similar to the app's name
        if not "/" in icon_path:
            icon_path = self.get_icon_path(icon_path)

        self.icon_path = icon_path

    def get_icon_path(self, icon_name):
        theme_icon = get_theme_icon(icon_name)
        if theme_icon:
            return theme_icon

        icon_path = self.path + "/icons"

        present_theme = []
        for _, _, files in os.walk(icon_path+"/Papirus-Dark"):  # This is weird but required to avoid an error from os.walk
            present_theme = files
            break
        if not present_theme:
            icon_path = icon_path + "/hicolor"
        else:
            icon_path = icon_path + "/Papirus-Dark"

        valid_icon_sizes = [imgdir for imgdir in next(os.walk(icon_path))[1] if (not "@" in imgdir)]  # Get all possible icon sizes
        valid_icon_sizes.remove('symbolic')  # Remove a redundant size option
        valid_icon_sizes = sorted(valid_icon_sizes, key=lambda icon_size: icon_size.split("x")[0], reverse=True)  # Sort from highest quality to lowest

        for icon_size in valid_icon_sizes:
            prefix = "/apps"
            if icon_size == "scalable":
                prefix = ""

            apps = []
            for _, _, files in os.walk(f"{icon_path}/{icon_size}{prefix}"):
                apps = files
                break
            if not apps:
                continue

            apps_names = ['.'.join(app.split(".")[:-1]).lower() for app in apps]
            if not icon_name.lower() in apps_names:
                continue

            return f"{icon_path}/{icon_size}{prefix}/{apps[apps_names.index(icon_name.lower())]}"

        return "image-missing"


xdg_data_dirs = get_xdg_data_dirs()

def generate_desktop_files_list():
    desktop_files = list()
    for data_dir in xdg_data_dirs:
        for application in xdg_data_dirs[data_dir]:
            application_file = dict()
            with open(f"{data_dir}/applications/{application}") as desktop_file:
                for line in desktop_file:
                    if len(application_file) >= 3:
                        break

                    line = line.split("=")
                    if not line[0] in ["Name", "Exec", "Icon"]:
                        continue

                    application_file[line[0]] = ''.join(line[1:]).rstrip('\n')

            try:
                desktop_files.append(DesktopFile(application_file['Name'], application_file['Exec'], data_dir, application_file['Icon']))
            except KeyError:
                pass
    return desktop_files


class DesktopApps:

    def __init__(self):
        self.desktop_files = []
        self.get_data()

    def assign_desktop_files(self, desktop_files):
        self.desktop_files = desktop_files

    def get_data(self):
        task = Utils.ThreadTask(target=generate_desktop_files_list, callback=lambda result, self=self: self.assign_desktop_files(result))
        task.run()


# Improve performance by using static typically used icon resolutions
# instead of fetching and processing them each time
