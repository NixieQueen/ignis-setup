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
from ignis import widgets as Widget
from ignis import utils as Utils
from ignis.services.niri import NiriService, NiriWorkspace
import asyncio

from utils.screennametoid import ScreennameToId
screennames = ScreennameToId.get_default()

niri = NiriService.get_default()
way_wm = niri


class WorkspaceButton(Widget.Button):
    def __init__(self, workspace: NiriWorkspace) -> None:
        self.workspace = workspace
        super().__init__(
            css_classes=["toppanel_workspace_button", "unset"],
            on_click=lambda _: self.switch_to(workspace.idx),
            on_right_click=lambda _: self.move_app_to(workspace.idx),
            halign="start",
            valign="center",
            child=Widget.Label(label=str(workspace.idx)),
        )
        if workspace.id == way_wm.active_window.workspace_id:
            self.add_css_class("active")

    def switch_to(self, workspace_id: int):
        #way_wm.send_command(f"dispatch workspace {workspace_name}")
        print(workspace_id)
        asyncio.create_task(Utils.exec_sh_async(f"niri msg action focus-workspace {workspace_id}"))

    def move_app_to(self, workspace_id: int, silent: bool=False):
        dispatcher = "move-window-to-workspace" if silent else "move-window-to-workspace"
        #way_wm.send_command(f"dispatch {dispatcher} {workspace_name}")
        asyncio.create_task(Utils.exec_sh_async(f"niri msg action {dispatcher} {workspace_id}"))
        

def scroll_workspaces(direction: str) -> None:
    current = way_wm.active_window.workspace_id
    if direction == "up":
        target = current - 1
        way_wm.switch_to_workspace(target)
    else:
        target = current + 1
        if target == 11:
            return
        way_wm.switch_to_workspace(target)


class Workspace(Widget.Box):
    def __init__(self, monitor_id: int=0):
        monitor_output = screennames.id_to_name(monitor_id)
        if way_wm.is_available:
            child = [
                Widget.EventBox(
                    on_scroll_up=lambda x: scroll_workspaces("up"),
                    on_scroll_down=lambda x: scroll_workspaces("down"),
                    css_classes=["toppanel_workspace"],
                    child=way_wm.bind_many(
                        ["workspaces", "active_window"],
                        transform=lambda workspaces, *_: [
                            WorkspaceButton(i) for i in workspaces if i.output == monitor_output
                        ],
                    ),
                )
            ]
        else:
            child = []
        super().__init__(child=child)
