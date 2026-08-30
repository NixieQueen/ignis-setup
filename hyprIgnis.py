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
# This is the start of my setup!
# Everything here is imported from the various subfolders.
# Then after importing all the various scripts they are all passed through an init.
# This init is per monitor so everything is started at once avoiding the need to repeat for loops
#
from ignis import utils
from ignis.css_manager import CssManager, CssInfoPath

import sys
sys.path.append(".")

# Importing the configs
from services import ConfigService, NiriConfigService
config = ConfigService.get_default()
NiriConfigService.get_default()

theme_name = str(config.get_value('theme'))
theme_path = f"{config._path}/themes/{theme_name}/theme.scss"

# app = IgnisApp.get_initialized()

css_manager = CssManager.get_default()
# Apply scss from a path
css_manager.apply_css(
    CssInfoPath(
        name=theme_name,
        path=theme_path,
        compiler_function=lambda compiler_path: utils.sass_compile(path=compiler_path),
    )
)

#
# Now it is time to import all our seperate modules and things
#

# Starting with some heavy utils that multiple functions may want to call
#from utils.desktopfiles import DesktopApps
#desktop_apps = DesktopApps(config._home_dir, config._path)  # This works, but figure out a way to call a function once this has finished!

from services import WallpaperService
WallpaperService.get_default()

# Loading services
#from services.musicservice import MusicService

# And ending on the actual modules themselves

from modules.top_panel import toppanel_creator
from modules.taskbar import taskbar_creator
from modules.side_panel import side_panel_creator
from modules.notifications import notification_popup

#
# Apps, defined as being modules that operate seperately from the desktop
#
from apps.applauncher import applauncher
from apps.quitmenu import quitmenu_creator
from apps.settingsapp import settings_creator

#
# And finally run the modules on all monitors
#

quitmenu_creator()
settings_creator(path=config._path)
for i in range(utils.get_n_monitors()):
    toppanel_creator(i)
    taskbar_creator(monitor_id=i)
    side_panel_creator(monitor_id=i)
    applauncher(monitor_id=i)
    notification_popup(monitor_id=i)
