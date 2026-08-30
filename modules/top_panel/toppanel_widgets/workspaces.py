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
from ignis import widgets
from ignis import utils as Utils
from ignis import variable
from ignis.services.niri import NiriService, NiriWorkspace
import asyncio

import extra_widgets
from services import ScreennameToId
screennames = ScreennameToId.get_default()

niri = NiriService.get_default()
way_wm = niri


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


class WorkspaceButton(extra_widgets.Button):
    def __init__(self, workspace: NiriWorkspace, indicator_target: variable.Variable) -> None:
        self.indicator_target = indicator_target
        self.workspace = workspace
        super().__init__(
            css_classes=["button"],
            on_click=lambda _: self.switch_to(workspace.idx),
            on_right_click=lambda _: self.move_app_to(workspace.idx),
            halign="center",
            valign="center",
        )
        if workspace.id in [active_workspace.id for active_workspace in way_wm.workspaces if active_workspace.is_active]:
            self.indicator_target.value = workspace.idx-1

    def switch_to(self, workspace_id: int):
        asyncio.create_task(Utils.exec_sh_async(f"niri msg action focus-workspace {workspace_id}"))
        self.indicator_target.value = workspace_id-1

    def move_app_to(self, workspace_id: int, silent: bool=False):
        dispatcher = "move-window-to-workspace" if silent else "move-window-to-workspace"
        #way_wm.send_command(f"dispatch {dispatcher} {workspace_name}")
        asyncio.create_task(Utils.exec_sh_async(f"niri msg action {dispatcher} {workspace_id}"))


class WorkspaceIndicator(widgets.Scale):

    def __init__(self):
        self.indicator_value = extra_widgets.animationVariable(value=0)

        super().__init__(
            css_classes=["slider"],
            min=0,
            max=1,
            step=1,
            value=self.indicator_value.bind('value', lambda x: x),
            sensitive=False,
            draw_value=False
        )


class WorkspaceWrapper(widgets.Overlay):

    def __init__(self, monitor_id: int):
        monitor_output = screennames.id_to_name(monitor_id)

        self.work_indicator = WorkspaceIndicator()
        
        self.size_hint = widgets.Box(
            spacing=10,
            css_classes=["button_wrapper"],
            child=way_wm.bind_many(
                ["workspaces"],
                transform=lambda workspaces, *_: [widgets.Box(css_classes=["button", "size_hint"]) for workspace in workspaces if workspace.output == monitor_output]
            )
        )
        self.buttons = widgets.Box(
            spacing=10,
            css_classes=["button_wrapper"],
            child=way_wm.bind_many(
                ["workspaces", "active_window"],
                transform=lambda workspaces, *_: self.get_buttons(workspaces, monitor_output)
            )
        )


        super().__init__(
            child=self.size_hint,
            overlays=[self.work_indicator, self.buttons]
        )

    def get_buttons(self, workspaces, monitor_output, *_):
        workspaces = [workspace for workspace in workspaces if workspace.output == monitor_output]
        self.work_indicator.max = len(workspaces)-1
        return [WorkspaceButton(i, self.work_indicator.indicator_value.target) for i in workspaces]
        

class Workspace(widgets.Box):
    def __init__(self, monitor_id: int=0):
        if way_wm.is_available:
            child = [
                widgets.EventBox(
                    on_scroll_up=lambda x: scroll_workspaces("up"),
                    on_scroll_down=lambda x: scroll_workspaces("down"),
                    css_classes=["toppanel", "workspace"],
                    child=[WorkspaceWrapper(monitor_id)],
                ),
            ]
        else:
            child = []
        super().__init__(child=child)
