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
import extra_widgets
from ignis.window_manager import WindowManager
from ignis import utils as Utils

from .grid_buttons import appGridButtons
from .search_bar import SearchBar
from .refresh_button import RefreshButton
from services import DesktopFileService, StaticApp


window_manager = WindowManager.get_default()
desktop_files = DesktopFileService.get_default()


def close_applauncher_windows():
    for i in range(Utils.get_n_monitors()):
        window_manager.close_window(f"ignis_applauncher_{i}")


class AppButton(extra_widgets.Button):
    def __init__(self, app: StaticApp):
        icon_box = Widget.Icon(image=app._icon_path, pixel_size=50)
        self.app = app

        super().__init__(
            child=icon_box,
            on_click=None,
            on_right_click=lambda _: self.applaunch(),
            css_classes=["applauncher", "app"],
            tooltip_text=app._class_name,
        )

    def applaunch(self):
        self.app.launch()
        Utils.Timeout(ms=600, target=close_applauncher_windows)


class AppGrid(Widget.Box):

    def __init__(self):
        self.page_index = -1
        self.apps = desktop_files.get_desktop_files()
        self.pages = dict()
        self.full_pages = dict()
        desktop_files.bind("signal::files_completed", lambda: self.update_pages())
        self.old_size_apps = 0
        self.page_size = 30
        self.icon_size = 50

        self.grid = Widget.Grid(
            column_num=10,
            child=Widget.Box()
        )
        self.grid_buttons = appGridButtons(appgrid=self)
        self.searchbar = SearchBar(appgrid=self)
        self._refresh_button = RefreshButton(lambda _: desktop_files.refresh_data())

        if self.apps:
            self.update_pages()

        super().__init__(
            vertical=True,
            child=[
                Widget.CenterBox(
                    start_widget=Widget.Box(),
                    center_widget=Widget.Box(child=[self.searchbar]),
                    end_widget=Widget.Box(child=[self._refresh_button]),
                    vertical=False
                ),
                self.grid,
                self.grid_buttons
            ]
        )

    def search_apps(self, search_prompt):  # Creates a small list of 'apps' that fit the search prompt and adds it to 'self.pages'
        search_prompt = search_prompt.lower()
        self.page_index = -1

        if not self.full_pages:
            return

        new_pages = list()
        # Go through 'full pages' and only take the files matching the prompt
        for page_number in self.full_pages:
            for appbutton in self.full_pages[page_number]:
                if search_prompt in appbutton.app._class_name:
                    new_pages.append(appbutton)

        self.pages = self.build_pages(new_pages) if len(new_pages) else []
        self.change_page(0)

    def reset_apps(self):  # Once a search has concluded the grid will be returned to its full view
        self.page_index = -1
        self.apps = desktop_files.get_desktop_files()
        self.pages = self.full_pages
        self.change_page(0)

    def update_pages(self):
        self.page_index = -1
        self.apps = desktop_files.get_desktop_files()

        pages = self.build_pages()
        self.pages = pages
        self.full_pages = pages

        print("update!")
        self.change_page(0)

    def change_page(self, new_page):  # Change the page index
        if not self.pages:
            self.grid.child = Widget.Box()
            self.grid_buttons.update_content()
            return

        if self.page_index == new_page:
            return

        if new_page > len(self.pages) - 1 or new_page < 0:
            return

        self.page_index = new_page
        self.grid.child = self.pages[new_page]
        self.grid_buttons.update_content()

    def build_pages(self, old_entries: list=[]):  # Gets called to construct a full grid of pages
        pages = dict()
        if not self.apps and not old_entries:
            return

        if not old_entries:
            size_apps = len(self.apps)
        else:
            size_apps = len(old_entries)
        full_pages = size_apps // self.page_size  # Returns a 'full page' per 30 apps

        if not old_entries:
            #if size_apps == self.old_size_apps:  # This is nice but does not work well with cache
            #    return self.pages
            self.old_size_apps = size_apps

        if not old_entries:
            self.processed_apps = [
                self.apps[page_app] for page_app in self.apps if self.apps[page_app]._icon_path != 'image-missing'
            ]
            size_apps = len(self.processed_apps)
        else:
            self.processed_apps = []
            
        for i in range(1, full_pages+1):
            if not old_entries:
                pages[i-1] = [
                    AppButton(app) for app in self.processed_apps[0+self.page_size*(i-1):self.page_size+self.page_size*(i-1)]
                ]
            else:
                pages[i-1] = [
                    old_entry for old_entry in old_entries[0+self.page_size*(i-1):self.page_size+self.page_size*(i-1)]
                ]

        if size_apps > full_pages * self.page_size:
            last_page_index = full_pages
            if not old_entries:
                pages[last_page_index] = [
                    AppButton(app) for app in self.processed_apps[0+self.page_size*last_page_index:]
                ]
            else:
                pages[last_page_index] = [
                    old_entry for old_entry in old_entries[0+self.page_size*last_page_index:]
                ]

        return pages
