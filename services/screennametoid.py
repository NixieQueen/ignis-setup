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
# Simple class holding names of all monitors and allows conversion to id
#
from ignis import utils as Utils
from .baseservice import BaseService


class ScreennameToId(BaseService):

    def __init__(self):
        self.screennames_ids = dict()
        self.screennames_names = dict()
        monitors = Utils.exec_sh('niri msg outputs | grep Output | cut -d"(" -f2').stdout
        for monitor in monitors.split("\n"):
            if not monitor:
                continue
            
            self.add_screen(monitor.rstrip(")"))
        super().__init__()

    def add_screen(self, name) -> None:
        keys = self.screennames_ids.keys()
        if name in keys:
            return

        id_screen = len(keys)
        self.screennames_ids[name] = id_screen
        self.screennames_names[id_screen] = name

    def name_to_id(self, name) -> int:
        if not name in self.screennames_ids.keys():
            name = 0

        return self.screennames_ids[name]

    def id_to_name(self, id):
        if not id in self.screennames_names.keys():
            id = 0

        return self.screennames_names[id]
