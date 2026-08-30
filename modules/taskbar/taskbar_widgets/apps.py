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
from ignis.menu_model import IgnisMenuModel, IgnisMenuItem
from ignis.window_manager import WindowManager
#from ignis.services.hyprland import HyprlandService
from ignis.services.niri import NiriService, NiriWindow
import extra_widgets
from services import ConfigService, DesktopIconService, DesktopFileService, PinnedAppsService, StaticApp, DynamicApp
from ignis.gobject import IgnisProperty, DataGObject


#hyprland = HyprlandService.get_default()
way_wm = NiriService.get_default()
window_manager = WindowManager.get_default()
config = ConfigService.get_default()
desktop_icons = DesktopIconService.get_default()
desktop_files = DesktopFileService.get_default()
pinned_apps = PinnedAppsService.get_default()


class ActivityIndicator(Widget.Box):

    def __init__(self, address_size: int):
        self._active = False
        super().__init__(
            css_classes=["taskbar_apps_separators"],
            halign="start",
            valign="center",
        )
        self.on_address_change(address_size)

    def on_address_change(self, address_size: int):
        padding_width = 1.7 / float(address_size) - 0.05 * (float(address_size) - 1)
        if padding_width < 0.2:
            padding_width = 0.2
        self.style = f"padding: 0.3rem {padding_width}rem;"

    def toggle_active(self, status: bool=False):
        if status == self._active:
            return
        
        if status:
            self.add_css_class('active')
        else:
            self.remove_css_class('active')
        self._active = status


class StaticAppButton(extra_widgets.Button):

    def __init__(self, app: StaticApp):
        self._app = app
        self._class_name = app._class_name
        icon = Widget.Icon(image=app._icon_path, pixel_size=46)
        menu = Widget.PopoverMenu(
            model=IgnisMenuModel(
                IgnisMenuItem(label="Launch", on_activate=lambda _: app.launch()),
                IgnisMenuItem(label="Unpin", on_activate=lambda _: app.unpin()),
            )
        )
        super().__init__(
            child=Widget.Box(child=[icon, menu]),
            on_click=lambda _: app.launch(),
            on_right_click=lambda _: menu.popup(),
            css_classes=["taskbar_apps", "pinned"],
            tooltip_text=self._class_name
        )
        self._button = self


class DynamicAppButton(DataGObject):

    def __init__(self, app: DynamicApp):
        super().__init__()
        self._app = app
        self._class_name = app._class_name
        self._address_size = 1
        
        self._icon = Widget.Icon(image=app._icon_path, pixel_size=46)
        self._menu = Widget.PopoverMenu(
            model=IgnisMenuModel(
                IgnisMenuItem(label="Close", on_activate=lambda _: app.close()),
                IgnisMenuItem(label="Pin", on_activate=lambda _: app.pin()),
            )
        )

        self._activity_indicators = [ActivityIndicator(1)]

        self._activity_box = Widget.CenterBox(
            center_widget=Widget.Box(
                spacing=3,
                child=self.bind(
                    "activity_box",
                    transform=lambda x: x
                )
            )
        )
        icon_box = Widget.Box(child=[self._icon, self._activity_box], vertical=True)
        self._button = extra_widgets.Button(
            child=Widget.Box(child=[icon_box, self._menu]),
            on_click=lambda _: app.focus(),
            on_right_click=lambda _: self._menu.popup(),
            css_classes=["taskbar_apps"],
            tooltip_text=self._class_name
        )

    @IgnisProperty
    def activity_box(self) -> list[ActivityIndicator]:
        return self._activity_indicators

    def on_address_change(self, addresses: list[int]):
        if self._app._addresses == addresses:
            return

        self._app._addresses = addresses
        self._app._address_index = 0

        address_size = len(addresses)
        if address_size == self._address_size:
            pass
            #return
        
        change = address_size - self._address_size
        self._address_size = address_size

        if change > 0:
            for i in range(0, change):
                self._activity_indicators.append(ActivityIndicator(address_size))
        else:
            for i in range(0, abs(change)):
                self._activity_indicators.pop()
        
        for activity_indicator in self._activity_indicators:
            activity_indicator.on_address_change(address_size)
        super().notify("activity_box")

    def get_client_address_index(self, client_id: int) -> int:
        return self._app._addresses.index(client_id)

    def null_focus(self):
        for activity_indicator in self._activity_indicators:
            activity_indicator.toggle_active(False)
            
    def update_focus(self, active_id: int):
        if not (active_id in self._app._addresses):
            return

        index = self.get_client_address_index(active_id)
        if index >= len(self._activity_indicators):
            return
        
        if self._activity_indicators[index]._active:
            return

        self.null_focus()

        self._activity_indicators[index].toggle_active(True)


class AppLauncher(extra_widgets.Button):
    def __init__(self, monitor_id):
        super().__init__(
            child=Widget.Icon(image="start-here-symbolic", pixel_size=56),
            on_click=lambda x: window_manager.open_window(f"ignis_applauncher_{monitor_id}"),
            css_classes=["taskbar_apps", "launcher"]
        )


class AppsBox(DataGObject):
    def __init__(self, vertical: bool=True):
        super().__init__()
        
        self._app_list: list[DynamicAppButton] | list[StaticAppButton] = []

        self._widget = Widget.Box(
            vertical=vertical,
            child=self.bind("app_list", transform=lambda x: [y._button for y in x])
        )

    @IgnisProperty
    def app_list(self) -> list[DynamicAppButton] | list[StaticAppButton]:
        return self._app_list

    def get_class_index(self, class_name: str) -> int:
        app_names = [app._class_name for app in self._app_list]
        return app_names.index(class_name)

    def change_address(self, class_name: str, addresses: list[int]):
        index = self.get_class_index(class_name)
        self._app_list[index].on_address_change(addresses)
        super().notify("app_list")
       
    def remove_class(self, class_name: str):
        if not (class_name in [app._class_name for app in self._app_list]):
            return
        
        index = self.get_class_index(class_name)
        # Something about having an app on ignis start causes it to be added twice!!!
        self._app_list.pop(index)
        super().notify("app_list")

    def add_app(self, app: DynamicAppButton | StaticAppButton):
        if app in self._app_list:
            return
        
        self._app_list.append(app)
        super().notify("app_list")
        #self.child = self._app_list

    
class Apps (Widget.Box):
    
    def __init__(self, monitor_id: int):
        vertical = True if config.get_value('taskbar_position') == 'unity' else False
        self._pinned_apps_cache: dict[str, StaticAppButton] = {}
        self._dynamic_apps_cache: dict[str, DynamicAppButton] = {}
        self._windows: list[NiriWindow] = []
        self._sorted_windows: dict[str, list[int]] = {}

        self._pinned_app_box = AppsBox(vertical)
        self._active_app_box = AppsBox(vertical)
        
        super().__init__(
            vertical = vertical,
            child=[
                AppLauncher(monitor_id), # The launcher button, as just one button
                self._pinned_app_box._widget,
                self._active_app_box._widget
                
            ]
        )

        for class_name in pinned_apps.get_pinned_apps():
            pinned_app = pinned_apps.get_pinned_apps()[class_name]
            pinned_app_box = StaticAppButton(pinned_app)
            self._pinned_apps_cache[class_name] = pinned_app_box
            self._pinned_app_box.add_app(pinned_app_box)
            
        # This is dumb, but to bind to these properties a widget is required :(
        Widget.Box(child=way_wm.bind(
            "windows",
            transform=lambda windows: [self.__on_windows_change(windows)]
        ))
        Widget.Box(child=way_wm.bind(
            "active_window",
            transform=lambda client: [self.__on_focus_change(client)]
        ))

    def get_window_name(self, window: NiriWindow) -> str:
        class_name = window.app_id or window.title
        class_split = class_name.split('_')
        if class_split[0] == 'steam' and len(class_split) == 3:
            class_name = window.title
        class_name = class_name.lower()

        if not (class_name in desktop_files.get_desktop_files()):
            for desktop_file_name in desktop_files.get_desktop_files():
                for symbol in ['-', ' ']:
                    if class_name in desktop_file_name.split(symbol):
                        class_name = desktop_file_name
        
        return class_name

    def sort_windows(self, windows: list[NiriWindow]) -> dict[str, list[int]]:
        sorted_windows = {}
        for w in windows:
            class_name = self.get_window_name(w)
        
            if not class_name in sorted_windows:
                sorted_windows[class_name] = []

            sorted_windows[class_name].append(w.id)
        
        return sorted_windows

    def add_window(self, class_name: str, addresses: list[int]):
        # Add new window to dynamic apps
        if class_name in self._dynamic_apps_cache:  # We already have it cached!
            self._dynamic_apps_cache[class_name].on_address_change(addresses)
            app_box = self._dynamic_apps_cache[class_name]
            
        else:
            app = desktop_files.generate_dynamic_app(class_name, addresses)
            app_box = DynamicAppButton(app)
            self._dynamic_apps_cache[class_name] = app_box

        self._active_app_box.add_app(app_box)

        # Remove window from pinned apps (if applicable)
        for app_box in self._pinned_app_box._app_list:
            if app_box._class_name != class_name:
                continue

            self._pinned_app_box.remove_class(class_name)

    def remove_window(self, class_name: str):
        # Remove window from dynamic apps
        self._active_app_box.remove_class(class_name)

        # Add it back to pinned apps if relevant
        if not (class_name in pinned_apps.get_pinned_apps()):
            return
        
        if class_name in self._pinned_apps_cache:
            pinned_app_box = self._pinned_apps_cache[class_name]
        else:
            pinned_app = pinned_apps.get_pinned_apps()[class_name]
            pinned_app_box = StaticAppButton(pinned_app)
            self._pinned_apps_cache[class_name] = pinned_app_box

        self._pinned_app_box.add_app(pinned_app_box)

    def __on_windows_change(self, windows: list[NiriWindow]):
        if windows == self._windows:
            return

        sorted_windows = self.sort_windows(windows)

        if len(self._sorted_windows) == len(sorted_windows):  # Only an address changed
            for class_name in self._sorted_windows:
                if len(self._sorted_windows[class_name]) == len(sorted_windows[class_name]):
                    continue

                self._active_app_box.change_address(class_name, sorted_windows[class_name])

            self._sorted_windows = sorted_windows
            self._windows = windows
            return

        self._sorted_windows = sorted_windows
        
        if len(self._windows) > len(windows):  # Subtracting windows
            for w in self._windows:
                if w in windows:
                    continue

                # Subtract window
                class_name = self.get_window_name(w)
                self.remove_window(class_name)
                
        else:  # Adding windows
            for w in windows:
                if w in self._windows:
                    continue

                # Add window
                class_name = self.get_window_name(w)
                self.add_window(class_name, self._sorted_windows[class_name])
                    
        self._windows = windows
        

    def __on_focus_change(self, client: NiriWindow):
        class_name = self.get_window_name(client)
        for w in self._active_app_box._app_list:
            if w._class_name != class_name:
                w.null_focus()
                continue

            w.update_focus(client.id)
            return
        
