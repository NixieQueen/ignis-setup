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
from ignis.services.hyprland import HyprlandService, HyprlandWorkspace

hyprland = HyprlandService.get_default()


class WorkspaceButton(Widget.Button):
    def __init__(self, workspace: HyprlandWorkspace) -> None:
        self.workspace = workspace
        super().__init__(
            css_classes=["toppanel_workspace_button", "unset"],
            on_click=lambda _: self.switch_to(self.get_workspace_name()),
            on_right_click=lambda _: self.move_app_to(self.get_workspace_name()),
            halign="start",
            valign="center",
            child=Widget.Label(label=str(workspace.name)),
        )
        if workspace.id == hyprland.active_workspace.id:
            self.add_css_class("active")

    def get_workspace_name(self):
        # Get around a hyprland bug that allows negative workspaces but cannot use them in commands
        if self.workspace.id <= 0:
            return self.workspace.name
        return self.workspace.id
            
    def switch_to(self, workspace_name: str):
        hyprland.send_command(f"dispatch workspace {workspace_name}")

    def move_app_to(self, workspace_name: str, silent: bool=False):
        dispatcher = "movetoworkspacesilent" if silent else "movetoworkspace"
        hyprland.send_command(f"dispatch {dispatcher} {workspace_name}")
        

def scroll_workspaces(direction: str) -> None:
    current = hyprland.active_workspace.id
    if direction == "up":
        target = current - 1
        hyprland.switch_to_workspace(target)
    else:
        target = current + 1
        if target == 11:
            return
        hyprland.switch_to_workspace(target)


class Workspace(Widget.Box):
    def __init__(self):
        if hyprland.is_available:
            child = [
                Widget.EventBox(
                    on_scroll_up=lambda x: scroll_workspaces("up"),
                    on_scroll_down=lambda x: scroll_workspaces("down"),
                    css_classes=["toppanel_workspace"],
                    child=hyprland.bind_many(
                        ["workspaces", "active_workspace"],
                        transform=lambda workspaces, *_: [
                            WorkspaceButton(i) for i in workspaces
                        ],
                    ),
                )
            ]
        else:
            child = []
        super().__init__(child=child)
