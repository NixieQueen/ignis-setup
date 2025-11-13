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
from ignis import utils as Utils

import os
from datetime import datetime

import asyncio

#from ignis.services.hyprland import HyprlandService
from ignis.services.niri import NiriService
#hyprland = HyprlandService.get_default()
niri = NiriService.get_default()
way_wm = niri


def get_time_data():
    n = datetime.now()
    return (n.month, n.hour)


class WallPaper:

    # Another module, retrieves wallpapers from the 'themes/.../activebackgrounds' folder
    # These wallpapers should be linked from the regular backgrounds folder by a settings panel
    # The naming convention is 'SeasonWeatherDaytime.png'
    # The default for this is 'default.png'

    def __init__(self, config):
        self.current_wallpaper = ""
        self.config = config
        self.time_data = get_time_data()

        self.wallpaper_path = f"{Utils.get_current_dir()}/../themes/{self.config['theme']}/activebackgrounds"
        self.wallpapers = self.get_wallpapers()

    def update_wallpaper(self):  # This is a function that is periodically called (once per hour or once per day)
        self.time_data = get_time_data()
        season = self.month_to_prefix()
        weather = self.weather_to_middix()
        daytime = self.hour_to_suffix()
        wallpaper = f"{season}{weather}{daytime}"

        wallpaper_names = [wallpaper.split(".")[0] for wallpaper in self.wallpapers]
        if not wallpaper in wallpaper_names:
            wallpaper = "default.png"
        else:
            wallpaper = self.wallpapers[wallpaper_names.index(wallpaper)]

        self.set_wallpaper(wallpaper)

    def get_wallpapers(self):
        wallpapers = []
        for path, dirs, files in os.walk(self.wallpaper_path):
            wallpapers = files
            break
        return wallpapers

    def set_wallpaper(self, wallpaper):
        if self.current_wallpaper == wallpaper:
            return

        full_wallpaper_path = f"{self.wallpaper_path}/{wallpaper}"


        #way_wm.send_command(f"dispatcher exec swww img {full_wallpaper_path} -t grow")
        #way_wm.send_command(f"action spawn-sh -- 'swww img {full_wallpaper_path} -t grow'")
        asyncio.create_task(Utils.exec_sh_async(f"swww img {full_wallpaper_path} -t grow"))
        self.current_wallpaper = wallpaper

    def hour_to_suffix(self):
        if not self.config['dwall_hour']:
            return 'Afternoon'

        hour = self.time_data[1]
        if self.config['dwall_hour_morning'] <= hour < self.config['dwall_hour_afternoon']:
            return 'Morning'

        if self.config['dwall_hour_afternoon'] <= hour < self.config['dwall_hour_evening']:
            return 'Afternoon'

        if self.config['dwall_hour_evening'] <= hour < self.config['dwall_hour_night']:
            return 'Evening'

        return 'Night'

    def weather_to_middix(self):
        # There is no weather implementation yet :(
        if not self.config['dwall_weather']:
            return 'Sunny'

        return 'Sunny'

    def month_to_prefix(self):
        if not self.config['dwall_season']:
            return 'Summer'

        month = self.time_data[0] % 12

        # Month is returned as a value between 0 and 12.
        # For the sake of making winter (month 12, 1 & 2)
        # a value easily handled we will just wrap 12 back to 0 :3

        if 0 <= month < 3:
            return 'Winter'

        if 3 <= month < 6:
            return 'Spring'

        if 6 <= month < 9:
            return 'Summer'

        return 'Autumn'


class WallpaperService(WallPaper):

    def __init__(self, config):
        super().__init__(
            config=config.config
        )
        # Timeout in milliseconds
        self.timeout = 3600000 if self.config['dwall_hour'] else 86400000
        self.poll = Utils.Poll(timeout=self.timeout, callback=lambda _: self.update_wallpaper())
