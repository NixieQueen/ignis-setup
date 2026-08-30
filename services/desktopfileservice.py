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
# A service for fetching desktopfiles and parsing the most important information (name, icon, execution command, etc)
from ignis import utils

from .baseservice import BaseService
from services import ConfigService
import asyncio
import os

from ignis.services.niri import NiriService


niri = NiriService.get_default()
config = ConfigService.get_default()


# Grab xdg_data_dirs and take only the applications
def get_xdg_data_dirs():
    # This is run once on startup to avoid having to wait on a shell command each time
    xdg_data_dirs = dict()

    var_xdg_data_dirs = utils.exec_sh("echo $XDG_DATA_DIRS").stdout.split(":")

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
xdg_data_dirs = get_xdg_data_dirs()


class App:

    def __init__(self, class_name: str, exec_cmd: str, icon_path: str):
        self._class_name = class_name
        self._exec_cmd = exec_cmd
        self._icon_path = icon_path
        
    def launch(self):
        asyncio.create_task(utils.exec_sh_async(f"niri msg action spawn-sh -- '{self._exec_cmd}'"))

        
class PinnedAppsService(BaseService):

    def __init__(self):
        self._cache_file = f"{config._path}/utils/pinned_apps.cache"
        self._pinned_apps = dict()

        super().__init__(
            signals=[
                "signal::app_added",
                "signal::app_removed"
            ]
        )

        try:
            self.read_cache()
        except FileNotFoundError:
            self.write_cache() 

    def read_cache(self) -> None:
        with open(self._cache_file, "r") as cache_file:
            for line in cache_file:
                line = line.rstrip('\n')
                if line == '':
                    continue
                
                class_name, exec_cmd, icon_path = line.split(' ||| ')
                self.add(class_name, exec_cmd, icon_path, False)
        cache_file.close()

    def write_cache(self) -> None:
        with open(self._cache_file, "w") as cache_file:
            cache_file.write('')
        cache_file.close()

        with open(self._cache_file, "a") as cache_file:
            for class_name in self._pinned_apps:
                cache_file.write(f"{class_name} ||| {self._pinned_apps[class_name]._exec_cmd} ||| {self._pinned_apps[class_name]._icon_path}\n")
        cache_file.close()

    def append_cache(self, class_name: str) -> None:
        with open(self._cache_file, "a") as cache_file:
            cache_file.write(f"{class_name} ||| {self._pinned_apps[class_name]._exec_cmd} ||| {self._pinned_apps[class_name]._icon_path}\n")
        cache_file.close()

    def add(self, class_name: str, exec_cmd: str, icon_path: str, add_to_cache: bool=True):
        if class_name in self._pinned_apps:
            return

        app = App(class_name, exec_cmd, icon_path)
        self._pinned_apps[class_name] = app
        if add_to_cache:
            self.emit("signal::app_added", app)
            self.append_cache(class_name)

    def remove(self, class_name: str):
        if not (class_name in self._pinned_apps):
            return

        self._pinned_apps.pop(class_name)
        self.emit("signal::app_removed", class_name)
        self.write_cache()

    def get_pinned_apps(self) -> dict:
        return self._pinned_apps


pinned_apps = PinnedAppsService.get_default()


class StaticApp(App):

    def __init__(self, class_name: str, exec_cmd: str, icon_path: str, xdg_dir: str):
        self._xdg_dir = xdg_dir
        super().__init__(class_name, exec_cmd, icon_path)

    def pin(self):
        pinned_apps.add(self._class_name, self._exec_cmd, self._icon_path)

    def unpin(self):
        pinned_apps.remove(self._class_name)


class DynamicApp(StaticApp):

    def __init__(self, class_name: str, exec_cmd: str, icon_path: str, xdg_dir: str, addresses: list=[]):
        self._addresses = addresses
        self._address_index = 0
        super().__init__(class_name, exec_cmd, icon_path, xdg_dir)

    def focus(self):
        if not self._addresses:
            return

        self._address_index = 0
        focused_address = niri.active_window.id
        if focused_address in self._addresses:
            self._address_index = self._addresses.index(focused_address)
            self._address_index = (self._address_index + 1) % len(self._addresses)  # Looping focus

        asyncio.create_task(utils.exec_sh_async(f"niri msg action focus-window --id {self._addresses[self._address_index]}"))

    def close(self):
        asyncio.create_task(utils.exec_sh_async(f"niri msg action close-window --id {self._addresses[self._address_index]}"))


class DesktopIconService(BaseService):

    def __init__(self):
        self._cache_file = f"{config._path}/utils/icon_cache.cache"
        self._theme_path = f"{config._path}/themes/{config.get_value('theme')}/apps"
        self._icon_theme_name = utils.exec_sh("gsettings get org.gnome.desktop.interface icon-theme").stdout.rstrip('\n')
        self._icon_theme_name = self._icon_theme_name.strip("'")
        self._theme_prefixes = ['apps', 'devices']
        self._icon_cache = dict()

        self._theme_icons = self.scrape_folder(self._theme_path)
        self._pixmap_icons = self.scrape_folder("/usr/share/pixmaps")

        self._queue = []
        try:
            self.read_cache()
        except FileNotFoundError:
            self.clear_cache()

        super().__init__()

    def read_cache(self) -> None:
        with open(self._cache_file, "r") as cache_file:
            for line in cache_file:
                line = line.rstrip('\n')
                if line == '':
                    continue
                
                icon_name, icon_path = line.split(' ||| ')
                self._icon_cache[icon_name] = icon_path
        cache_file.close()

    def clear_cache(self) -> None:
        with open(self._cache_file, "w") as cache_file:
            cache_file.write('')
        cache_file.close()

    def append_cache(self, icon_name: str, icon_path: str) -> None:
        with open(self._cache_file, "a") as cache_file:
            cache_file.write(f"{icon_name} ||| {icon_path}\n")
        cache_file.close()
        
    def add_to_queue(self, icon_name: str, xdg_dir: str="/usr/share"):
        if icon_name in self._icon_cache:
            return
        
        self._queue.append((icon_name, xdg_dir))

    def parse_individual_icon(self, icon_name: str, xdg_dir: str="/usr/share"):
        if icon_name in self._icon_cache:
            return

        icon_path = self.parse_icon(icon_name, xdg_dir)
        if not icon_path:
            return

        self._icon_cache[icon_name] = icon_path
        self.append_cache(icon_name, icon_path)
        
    def parse_queue(self):
        for entry in self._queue:
            icon_path = self.parse_icon(entry[0], entry[1])
            if not icon_path:
                continue

            self._icon_cache[entry[0]] = icon_path
            self.append_cache(entry[0], icon_path)
            
        self._queue = []

    def get_icon_path(self, icon_name: str, class_name: str="") -> str:
        '''
        Returns the path of an icon, can be given a classname to instead
        return the path of an icon while evaluating the 'in-flight' icon.
        In this case the ignis theme icon still takes priority!
        '''
        if not class_name:
            if not (icon_name in self._icon_cache):
                return f"{self._theme_path}/default.svg"

            return self._icon_cache[icon_name]
        else:
            icon_path = self.get_theme_icon_path(class_name)
            if not icon_path:
                icon_path = utils.get_app_icon_name(class_name)
                if not icon_path:
                    icon_path = self.get_icon_path(icon_name)
                    if not icon_path:
                        return f"{self._theme_path}/default.svg"
            return icon_path                

    def get_theme_icon_path(self, icon_name: str) -> str:
        if not (icon_name in self._theme_icons):
            return ""
        
        return self._theme_icons[icon_name]

    def get_pixmap_icon_path(self, icon_name: str) -> str:
        if not (icon_name in self._pixmap_icons):
            return ""

        return self._pixmap_icons[icon_name]

    def walk_through_icon_folder(self, icon_name: str, folder: str) -> str:
        folders = []
        for _, folders, _ in os.walk(folder):
            folders = folders
            break
        if not folders:
            return ""

        valid_icon_sizes = [imgdir for imgdir in folders if (not "@" in imgdir)]  # Get all possible icon sizes

                
        if 'symbolic' in valid_icon_sizes:
            valid_icon_sizes.remove('symbolic')  # Remove a redundant size option

        valid_icon_sizes = sorted(valid_icon_sizes, key=lambda icon_size: icon_size.split("x")[0], reverse=True)  # Sort from highest quality to lowest

        for icon_size in valid_icon_sizes:
            #if icon_size == "scalable":
            #    prefix = ""
            for theme_prefix in self._theme_prefixes:
                apps = []
                for _, _, files in os.walk(f"{folder}/{icon_size}/{theme_prefix}"):
                    apps = files
                    break
                if not apps:
                    continue
            
                apps_names = ['.'.join(app.split(".")[:-1]) for app in apps]
                if not icon_name in apps_names:
                    continue
            
                return f"{folder}/{icon_size}/{theme_prefix}/{apps[apps_names.index(icon_name)]}"
        return ""
        
    def get_xdg_icon_path(self, icon_name: str, xdg_dir: str) -> str:
        icon_path = ""

        # Try the installed theme folder first
        icon_path = self.walk_through_icon_folder(icon_name, f"{config._home_dir}/.icons/{self._icon_theme_name}")

        if not icon_path:
            # Try the xdg dir next
            icon_path = self.walk_through_icon_folder(icon_name, f"{xdg_dir}/icons/hicolor")

        return icon_path        

    def scrape_folder(self, folder: str) -> dict:
        theme_icons = dict()
        icons = []
        for _, _, files in os.walk(folder):
            icons = files
            break
        if not icons:
            return theme_icons

        for icon in icons:
            icon_name = '.'.join(icon.split(".")[:-1])
            theme_icons[icon_name] = f"{folder}/{icon}"
        return theme_icons
    
    def parse_icon(self, icon_name: str, xdg_dir: str) -> str:
        icon_path = ""

        # Attempt to find the icon in the theme folder
        icon_path = self.get_theme_icon_path(icon_name)

        if not icon_path:
            # Find it in pixmaps instead
            icon_path = self.get_pixmap_icon_path(icon_name)

            if not icon_path:
                # Do the most expensive search :(, go through xdg path
                icon_path = self.get_xdg_icon_path(icon_name, xdg_dir)

        return icon_path

    
desktop_icons = DesktopIconService.get_default()
            

class DesktopFileService(BaseService):

    def __init__(self):
        self._cache_file = f"{config._path}/utils/desktop_files.cache"
        self._desktop_file_cache = dict()

        self._running = True
        self._default_sleep_time = 0.5
        self._sleep_time = self._default_sleep_time
        
        super().__init__(
            signals=[
                "signal::files_completed"
            ]
        )

        try:
            self.read_cache()
        except FileNotFoundError:
            self.write_cache()
        asyncio.create_task(self.parse_desktop_files())

    def get_desktop_files(self) -> dict:
        return self._desktop_file_cache
        
    def read_cache(self) -> None:
        with open(self._cache_file, "r") as cache_file:
            for line in cache_file:
                line = line.rstrip('\n')
                if line == '':
                    continue
                
                class_name, exec_cmd, icon_path, xdg_dir = line.split(' ||| ')
                self._desktop_file_cache[class_name] = StaticApp(class_name, exec_cmd, icon_path, xdg_dir)
        cache_file.close()

    def write_cache(self) -> None:
        with open(self._cache_file, "w") as cache_file:
            cache_file.write('')
        cache_file.close()

        with open(self._cache_file, "a") as cache_file:
            for app_name in self._desktop_file_cache:
                app = self._desktop_file_cache[app_name]
                cache_file.write(f"{app._class_name} ||| {app._exec_cmd} ||| {app._icon_path} ||| {app._xdg_dir}\n")
        cache_file.close()

    def append_cache(self, app: StaticApp) -> None:
        with open(self._cache_file, "a") as cache_file:
            cache_file.write(f"{app._class_name} ||| {app._exec_cmd} ||| {app._icon_path} ||| {app._xdg_dir}\n")
        cache_file.close()

    def generate_dynamic_app(self, class_name: str, addresses: list=[]):
        print("Generating dynamic app!")
        if not (class_name in self._desktop_file_cache):
            image = desktop_icons.get_icon_path(class_name, class_name)
            if image.split("/")[-1] == "default.svg":
                desktop_icons.parse_individual_icon(class_name)
                image = desktop_icons.get_icon_path(class_name, class_name)
            return DynamicApp(class_name, "", image if image else "image-missing", "", addresses)

        static_app = self._desktop_file_cache[class_name]
        return DynamicApp(class_name, static_app._exec_cmd, static_app._icon_path, static_app._xdg_dir, addresses)

    async def unclutter_exec(self, exec_cmd):
        # The exec command of desktop files is often quite cluttered with extra arguments.
        # The following seeks to remove as much clutter as possible
        # May  result in broken exec commands!
        exec_cmd = exec_cmd.split(' ')
        exec_cmd = [exec_cmd_part for exec_cmd_part in exec_cmd if exec_cmd_part != '']
        exec_cmd = [exec_cmd_part for exec_cmd_part in exec_cmd if exec_cmd_part[0] != '%' and (exec_cmd_part[0:2] != '--' or exec_cmd_part == '--gui')]
        exec_cmd = ' '.join(exec_cmd)
        return exec_cmd

    async def read_desktop_file(self, desktop_file_path: str) -> dict | None:
        # If not, open the file and catalogue it
        app_file = dict()
        broken_file = False
        with open(desktop_file_path) as desktop_file:
            for line in desktop_file:
                if line != '[Desktop Entry]\n' and line.startswith('['):
                    break

                if len(app_file) >= 4:
                    break

                line = line.split("=")
                if not line[0] in ["Name", "Exec", "Icon", "NoDisplay"]:
                    continue

                if line[0] == "NoDisplay":
                    no_display = ''.join(line[1:]).rstrip('\n')
                    if no_display == '1' or no_display == 'true':
                        broken_file = True
                        break

                app_file[line[0]] = ''.join(line[1:]).rstrip('\n')

        if broken_file or len(app_file) < 3:
            return

        app_file['Exec'] = await self.unclutter_exec(app_file['Exec'])
        app_file['Name'] = app_file['Name'].lower()

        return app_file

    def refresh_data(self):
        if self._running:
            return

        self._running = True
        self._sleep_time = 0.01
        self._desktop_file_cache = dict()
        self.emit("signal::files_completed")
        asyncio.create_task(self.parse_desktop_files())

    async def parse_desktop_files(self):
        desktop_file_cache = dict()
        queue = []
        iconless_queue = []
        for data_dir in xdg_data_dirs:
            for desktop_file in xdg_data_dirs[data_dir]:
                await asyncio.sleep(self._sleep_time)
                desktop_file = f"{data_dir}/applications/{desktop_file}"
                desktop_file_data = await self.read_desktop_file(desktop_file)
                if not desktop_file_data:
                    continue
                                
                #if desktop_file_data['Name'] in self._desktop_file_cache:
                #    continue

                desktop_file_data['Datadir'] = data_dir
                
                if desktop_file_data['Icon'].split('.')[-1] in ['png', 'svg', 'jpg']:
                    queue.append(desktop_file_data)
                    continue

                iconless_queue.append(desktop_file_data)
                desktop_icons.add_to_queue(desktop_file_data['Icon'], data_dir)

        desktop_icons.parse_queue()
        for entry in iconless_queue:
            entry['Icon'] = desktop_icons.get_icon_path(entry['Icon'])
            queue.append(entry)

        for entry in queue:
            await asyncio.sleep(self._sleep_time)
            app = StaticApp(entry['Name'], entry['Exec'], entry['Icon'], entry['Datadir'])
            desktop_file_cache[entry['Name']] = app
            
        self._desktop_file_cache = desktop_file_cache
        self.write_cache()

        self._sleep_time = self._default_sleep_time
        self._running = False
        self.emit("signal::files_completed")
