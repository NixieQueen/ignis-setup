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
from ignis import utils as Utils
from ignis.css_manager import CssManager, CssInfoPath
from utils.ignisconfig import Config

import sys
sys.path.append(".")

path = Utils.get_current_dir()
config = Config(path)
theme_name = config.config['theme']
theme_path = f"{path}/themes/{theme_name}/{theme_name}theme.scss"

# app = IgnisApp.get_initialized()

css_manager = CssManager.get_default()
# Apply scss from a path
css_manager.apply_css(
    CssInfoPath(
        name=theme_name,
        path=theme_path,
        compiler_function=lambda compiler_path: Utils.sass_compile(path=compiler_path),
    )
)


#
# Now it is time to import all our seperate modules and things
#

# Starting with some heavy utils that multiple functions may want to call
from utils.desktopicons import DesktopApps
#desktop_apps = DesktopApps()  # This works, but figure out a way to call a function once this has finished!

# And ending on the actual modules themselves

from modules.top_panel import toppanel_creator
from modules.taskbar import taskbar_creator

#
# And finally run the modules on all monitors
#

for i in range(Utils.get_n_monitors()):
    print(i)
    toppanel_creator(i)
    taskbar_creator(monitor_id=i, config=config)
