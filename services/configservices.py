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
# Handling configs for Ignis and Niri as a service!
#
from typing import Any

from services.baseservice import BaseService
from utils import Config, NiriConfigManager
from ignis import utils

path = '/'.join(utils.get_current_dir().split('/')[:-1])
home_dir = '/'.join(path.split('/')[0:3])


class ConfigService(BaseService):

    def __init__(self) -> None:
        self._path = path
        self._home_dir = home_dir
        self._config = Config(path)

        super().__init__(
            signals=[
                "signal::config_changed"
            ]
        )

    def set_value(self, entry: str, value: str | bool | int) -> None:
        if not (entry in self._config.config):
            return

        self._config.config[entry] = value
        self.emit("signal::config_changed", entry, value)

    def get_value(self, entry: str) -> Any:
        if not (entry in self._config.config):
            return None

        return self._config.config[entry]

    def write_config(self):
        self._config.write_config()


class NiriConfigService(BaseService):

    def __init__(self):
        self._home_dir = home_dir
        self._niri_config = NiriConfigManager(home_dir)

        super().__init__(
            signals=[
                "signal::niriconfig_changed"
            ]
        )

    def merge(self):
        self._niri_config.merge()

    def write_monitor_config(self, monitor_config: list):
        self._niri_config.write_monitor_config(monitor_config)

    def write_blur_config(self):
        self._niri_config.write_blur_config()

    def assign_config_value(self, index: str, value: str | int | float | bool):
        self._niri_config.assign_config_value(index, value)
        self.emit("signal::niriconfig_changed", index, value)

    def get_value(self, index: str):
        if not (index in self._niri_config._config):
            return

        return self._niri_config._config[index]
