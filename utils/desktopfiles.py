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
from services import ConfigService
import os
import time

from .themeicons import get_theme_icon

config = ConfigService.get_default()


# Grab xdg_data_dirs and take only the applications
def get_xdg_data_dirs():
    # This is run once on startup to avoid having to wait on a shell command each time
    xdg_data_dirs = dict()

    var_xdg_data_dirs = Utils.exec_sh("echo $XDG_DATA_DIRS").stdout.split(":")

    for data_dir in var_xdg_data_dirs:
        data_dir = data_dir.rstrip('\n')
        applications = []
        for _, _, files in os.walk(data_dir+"/applications"):
            applications = [app for app in files if app.split(".")[-1] == "desktop"]
            break
        if not applications:
            continue

        xdg_data_dirs[data_dir] = applications
    return xdg_data_dirs


def walk_through_icon_path(icon_name: str, path: list, suffix: str="/icons"):
    # This should ask for the gtk_icon_theme variable, however for now Papirus-Dark will be assumed
    for theme_folder in ['Papirus', 'hicolor']:
        for upper_folder in path:  # Search through every directory in xdg but give priority to the desktopfile folder
            icon_path = upper_folder + suffix
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
    return


def search_pixmaps(icon_name: str):
    apps = []
    for _, _, files in os.walk(f"/usr/share/pixmaps"):
        apps = files
        break
    if not apps:
        return

    apps_names = ['.'.join(app.split(".")[:-1]).lower() for app in apps]
    if not icon_name.lower() in apps_names:
        return

    return f"/usr/share/pixmaps/{apps[apps_names.index(icon_name.lower())]}"


def get_icon_path(icon_name: str, theme: str, home_dir: str, path: str, xdg_data_dirs: list):
    icon_name = '.'.join([i for i in icon_name.split('.') if i != 'png'])
    theme_icon = get_theme_icon(icon_name, theme)
    if theme_icon:
        return theme_icon

    for valid_path in [([home_dir],"/.icons"), ([path] + xdg_data_dirs, "/icons")]:
        icon = walk_through_icon_path(icon_name, valid_path[0], valid_path[1])
        if icon:
            return icon

    icon = search_pixmaps(icon_name)
    if icon:
        return icon

    #print(f"{icon_name} and {theme} and {path} and {xdg_data_dirs}")        
    return "image-missing"


class DesktopFile:

    def __init__(self, name: str, exec_cmd: str, home_dir: str, path: str, icon_path: str, xdg_data_dirs: list):
        self.name = name
        self.exec_cmd = exec_cmd
        self.path = path

        self.xdg_data_dirs = xdg_data_dirs
        self.xdg_data_dirs.pop(xdg_data_dirs.index(path))

        # icon_path can either be a path, or more likely, a name similar to the app's name
        if not "/" in icon_path:
            icon_path = get_icon_path(icon_path, config.get_value('theme'), home_dir, path, xdg_data_dirs)

        self.icon_path = icon_path

class DesktopApps:

    def __init__(self, home_dir: str, path: str):
        self.home_dir = home_dir
        self._sleep_timer = 0.5
        self._cache_file = f"{path}/utils/desktop_file.cache"
        self.desktop_files = Variable(value=[])
        self.xdg_data_dirs = get_xdg_data_dirs()
        self.task = Utils.ThreadTask(
            target=self.generate_desktop_files_list,
            callback=lambda result, self=self: self.assign_desktop_files(result)
        )
        self._task_finished = True
        self.get_data()

    def assign_desktop_files(self, desktop_files, write_cache: bool=True):
        if self.desktop_files.value == desktop_files:
            return
        
        self.desktop_files.value = desktop_files
        if write_cache:
            self.write_cache()

    def get_data(self):
        try:
            self.read_cache()
        except FileNotFoundError:
            pass
        self._task_finished = False
        self.task.run()

    def refresh_data(self):
        if not self._task_finished:
            return
        
        self._sleep_timer = 0.05
        self.desktop_files.value = []
        self._task_finished = False
        self.task.run()

    def read_cache(self):
        cache_files = list()
        with open(self._cache_file, "r") as cache_file:
            for line in cache_file:
                line = line.rstrip('\n')
                line = line.split(" ||| ")

                if len(line) < 4:
                    continue
                
                cache_files.append(
                    DesktopFile(
                        line[0],
                        line[1],
                        self.home_dir,
                        line[2],
                        line[3],
                        list(self.xdg_data_dirs.keys())
                    )
                )

        if not cache_files:
            return

        self.assign_desktop_files(cache_files, write_cache=False)
        
    def write_cache(self):
        if not self.desktop_files.value:
            return
        
        with open(self._cache_file, "w") as cache_file:
            cache_file.write("")

        with open(self._cache_file, "a") as cache_file:
            for item in self.desktop_files.value:
                name = item.name
                exec_cmd = item.exec_cmd
                data_dir = item.path
                icon_path = item.icon_path
                
                cache_file.write(f"{name} ||| {exec_cmd} ||| {data_dir} ||| {icon_path}\n")

    def generate_desktop_files_list(self):
        desktop_files = list()
        for data_dir in self.xdg_data_dirs:
            for application in self.xdg_data_dirs[data_dir]:
                # Add a delay to not overwhelm cpus
                time.sleep(self._sleep_timer)
                # Check to see if we already have this desktop file cached
                desktop_file_names = [desktop_file.name.lower() for desktop_file in self.desktop_files.value]
                application_name = ".".join(application.split(".")[:-1]).lower()
                if application_name in desktop_file_names:
                    desktop_files.append(self.desktop_files.value[desktop_file_names.index(application_name)])
                    continue

                # If not, open the file and catalogue it
                application_file = dict()
                broken_file = False
                with open(f"{data_dir}/applications/{application}") as desktop_file:
                    for line in desktop_file:
                        if line != '[Desktop Entry]\n' and line.startswith('['):
                            break

                        if len(application_file) >= 4:
                            break

                        line = line.split("=")
                        if not line[0] in ["Name", "Exec", "Icon", "NoDisplay"]:
                            continue

                        if line[0] == "NoDisplay":
                            no_display = ''.join(line[1:]).rstrip('\n')
                            if no_display == '1' or no_display == 'true':
                                broken_file = True
                                break

                        application_file[line[0]] = ''.join(line[1:]).rstrip('\n')

                try:
                    if broken_file:
                        continue
                    
                    if application_file['Name'].lower() in [page_app.name.lower() for page_app in desktop_files]:
                        continue

                    # The exec command of desktop files is often quite cluttered with extra arguments.
                    # The following seeks to remove as much clutter as possible
                    # May  result in broken exec commands!
                    exec_cmd = application_file['Exec'].split(' ')
                    exec_cmd = [exec_cmd_part for exec_cmd_part in exec_cmd if exec_cmd_part != '']
                    exec_cmd = [exec_cmd_part for exec_cmd_part in exec_cmd if exec_cmd_part[0] != '%' and (exec_cmd_part[0:2] != '--' or exec_cmd_part == '--gui')]
                    exec_cmd = ' '.join(exec_cmd)

                    desktop_files.append(
                        DesktopFile(
                            application_file['Name'],
                            exec_cmd,
                            self.home_dir,
                            data_dir,
                            application_file['Icon'],
                            list(self.xdg_data_dirs.keys())
                        )
                    )
                except KeyError:
                    print("Desktop file with incomplete data found!\n")
                    print(f"{application_file["Name"]}\n{data_dir}\n")
                    pass
        
        self._sleep_timer = 0.5
        self._task_finished = True
        return desktop_files



# Improve performance by using static typically used icon resolutions
# instead of fetching and processing them each time
