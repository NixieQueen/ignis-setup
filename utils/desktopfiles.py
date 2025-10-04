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
from ignis.variable import Variable
import os

from .themeicons import get_theme_icon


# Grab xdg_data_dirs and take only the applications
def get_xdg_data_dirs():
    # This is run once on startup to avoid having to wait on a shell command each time
    xdg_data_dirs = dict()

    var_xdg_data_dirs = Utils.exec_sh("echo $XDG_DATA_DIRS").stdout.split(":")

    for data_dir in var_xdg_data_dirs:
        data_dir = data_dir.rstrip('\n')
        applications = []
        for path, dirs, files in os.walk(data_dir+"/applications"):
            applications = [app for app in files if app.split(".")[-1] == "desktop"]
            break
        if not applications:
            continue

        xdg_data_dirs[data_dir] = applications
    return xdg_data_dirs


def get_icon_path(icon_name: str, theme: str, path: str, xdg_data_dirs: list):
        theme_icon = get_theme_icon(icon_name, theme)
        if theme_icon:
            return theme_icon


        # This should ask for the gtk_icon_theme variable, however for now Papirus-Dark will be assumed
        for theme_folder in ['Papirus-Dark', 'hicolor']:
            for upper_folder in [path] + xdg_data_dirs:  # Search through every directory in xdg but give priority to the desktopfile folder
                icon_path = upper_folder + "/icons"
                folders = []
                for _, folders, _ in os.walk(f"{icon_path}/{theme_folder}"):
                    folders = folders
                    break
                if not folders:
                    continue

                icon_path = icon_path + "/" + theme_folder

                valid_icon_sizes = [imgdir for imgdir in folders if (not "@" in imgdir)]  # Get all possible icon sizes
                if 'symbolic' in valid_icon_sizes:
                    valid_icon_sizes.remove('symbolic')  # Remove a redundant size option

                valid_icon_sizes = sorted(valid_icon_sizes, key=lambda icon_size: icon_size.split("x")[0], reverse=True)  # Sort from highest quality to lowest

                for icon_size in valid_icon_sizes:
                    prefix = "/apps"
                    #if icon_size == "scalable":
                    #    prefix = ""

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


class DesktopFile:

    def __init__(self, name: str, exec_cmd: str, path: str, icon_path: str, config, xdg_data_dirs: list):
        self.name = name
        self.exec_cmd = exec_cmd
        self.path = path

        self.config = config
        self.xdg_data_dirs = xdg_data_dirs
        self.xdg_data_dirs.pop(xdg_data_dirs.index(path))

        # icon_path can either be a path, or more likely, a name similar to the app's name
        if not "/" in icon_path:
            icon_path = get_icon_path(icon_path, config.config['theme'], path, xdg_data_dirs)

        self.icon_path = icon_path

class DesktopApps:

    def __init__(self, config):
        self.config = config
        self.desktop_files = Variable(value=[])
        self.xdg_data_dirs = get_xdg_data_dirs()
        self.task = Utils.ThreadTask(
            target=self.generate_desktop_files_list,
            callback=lambda result, self=self: self.assign_desktop_files(result)
        )
        self.get_data()

    def assign_desktop_files(self, desktop_files):
        self.desktop_files.value = desktop_files

    def get_data(self):
        self.task.run()

    def generate_desktop_files_list(self):
        desktop_files = list()
        for data_dir in self.xdg_data_dirs:
            for application in self.xdg_data_dirs[data_dir]:
                # Check to see if we already have this desktop file cached
                desktop_file_names = [desktop_file.name.lower() for desktop_file in self.desktop_files.value]
                application_name = ".".join(application.split(".")[:-1]).lower()
                if application_name in desktop_file_names:
                    desktop_files.append(self.desktop_files.value[desktop_file_names.index(application_name)])
                    continue

                # If not, open the file and catalogue it
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
                    if application_file['Name'].lower() in [page_app.name.lower() for page_app in desktop_files]:
                        continue

                    # The exec command of desktop files is often quite cluttered with extra arguments.
                    # The following seeks to remove as much clutter as possible
                    # May  result in broken exec commands!
                    exec_cmd = application_file['Exec'].split(' ')
                    exec_cmd = [exec_cmd_part for exec_cmd_part in exec_cmd if exec_cmd_part[0] != '%' and (exec_cmd_part[0:2] != '--' or exec_cmd_part == '--gui')]
                    exec_cmd = ' '.join(exec_cmd)

                    desktop_files.append(
                        DesktopFile(
                            application_file['Name'],
                            exec_cmd,
                            data_dir,
                            application_file['Icon'],
                            self.config,
                            list(self.xdg_data_dirs.keys())
                        )
                    )
                except KeyError:
                    pass
        return desktop_files



# Improve performance by using static typically used icon resolutions
# instead of fetching and processing them each time
