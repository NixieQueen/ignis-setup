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
from ..elements import (
    SettingsNavigation, SettingsPage,
    SubHeaderEntry, SwitchEntry,
    SliderEntry, InputboxEntry,
    DropdownEntry
)
from ignis import utils
from services import NiriConfigService
import asyncio


niriconfig = NiriConfigService.get_default()


class MonitorPage(SettingsNavigation):

    def __init__(self, active_screen):
        self.pages = []
        self.active_screen = active_screen

        '''
        dict is made up of name, on/off, mode (resolution@refresh_rate),
        scale, rotation and position

        'name': str
        'displayname': str
        'status': bool
        'mode': str ([x]x[y]@[z])
        'available modes': list ^
        'scale': str (float 1.1)
        'rotation': str (normal, 90, 180, 270, flipped, flipped-90, flipped-180, flipped-270)
        'position': str (x=int y=int)
        '''
        self._monitor_config = list()
        self._monitor_entries = list()
        
        self._page = SettingsPage(
            name='Monitors',
            apply_function=lambda _: self.apply_function(),
            save_function=lambda _: self.save_function(),
            children=self._monitor_entries,
            spacing=5
        )
        
        super().__init__(
            icon_image="video-display-symbolic",
            onclick=lambda _: self.clicked(),
            tooltip_text="Monitor setup"
        )

        asyncio.create_task(self.populate_monitor_entries())

    def change_settings(self, monitor_id: int, setting: str, value: str | int | bool | None) -> None:
        if value == None:
            return
        self._monitor_config[monitor_id][setting] = value
        
    async def parse_niri_outputs(self) -> None:
        if self._monitor_config:
            return
        
        monitors = utils.exec_sh("niri msg outputs").stdout
        monitors = monitors.split("Output")
        for monitor in monitors:
            config_entry = {
                "name": "",
                "displayname": "",
                "status": True,
                "mode": "",
                "available modes": [],
                "scale": "",
                "rotation": "",
                "posx": "",
                "posy": ""
            }
            modes = False
            for line in monitor.split("\n"):
                if not line:
                    continue

                if modes:
                    if "current" in line:
                        config_entry["mode"] = line.split(" (")[0].strip(" ")
                    config_entry["available modes"].append(line.split(" (")[0].strip(" "))
                    continue

                if not config_entry["name"]:
                    line = line.split('" ')
                    config_entry["displayname"] = line[0].strip('" ')
                    config_entry["name"] = line[1].strip('()')
                    continue

                if "Disabled" in line:
                    config_entry["status"] = False
                    continue

                line = line.split(": ")
                if "Logical position" in line[0]:
                    x, y = line[1].split(", ")
                    config_entry["posx"] = x
                    config_entry["posy"] = y

                elif "Scale" in line[0]:
                    config_entry["scale"] = line[1]
                    
                elif "Transform" in line[0]:
                    config_entry["rotation"] = line[1]
                    
                elif "Available modes" in line[0]:
                    modes = True
                
            if config_entry["name"]:
                self._monitor_config.append(config_entry)

    async def populate_monitor_entries(self) -> None:
        await self.parse_niri_outputs()
        i = 0
        for monitor in self._monitor_config:
            self._monitor_entries.append(SubHeaderEntry(monitor["displayname"]))
            self._monitor_entries.append(SwitchEntry("Disable monitor", lambda x, i=i: self.change_settings(i, "status", x.clicked), monitor["status"]))
            self._monitor_entries.append(DropdownEntry("Resolution & refreshrate", lambda _, x, i=i: self.change_settings(i, "mode", x), monitor["available modes"], monitor["mode"]))
            self._monitor_entries.append(SliderEntry("Scale", lambda x, i=i: self.change_settings(i, "scale", str(round(x.value, 1))), 1, 2, 0.1, float(monitor["scale"])))
            self._monitor_entries.append(
                DropdownEntry(
                    "Rotation",
                    lambda _, x, i=i: self.change_settings(i, "rotation", x),
                    ["normal", "90", "180", "270", "flipped", "flipped-90", "flipped-180", "flipped-270"],
                    monitor["rotation"]
                )
            )
            self._monitor_entries.append(InputboxEntry("X position of monitor", lambda x, i=i: self.change_settings(i, "posx", self.check_numeric_validity(x.text)), monitor["posx"]))
            self._monitor_entries.append(InputboxEntry("Y position of monitor", lambda x, i=i: self.change_settings(i, "posy", self.check_numeric_validity(x.text)), monitor["posy"]))
            i += 1
        self._page.update_content(self._monitor_entries)

    def check_numeric_validity(self, text):
        if not text.strip('-').isnumeric():
            return None

        if "-" in text[1:]:
            return None

        return text
        

    def apply_function(self):
        self.save_function()
        niriconfig.merge()

    def save_function(self):
        niriconfig.write_monitor_config(self._monitor_config)

    def clicked(self) -> None:
        for page in self.pages:
            page.deactivate()

        self.activate()
        self.active_screen.set_value(self._page)
        
