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
from modules.taskbar.taskbar_widgets.apps import AppButton, App


class AppGrid(Widget.Grid):

    def __init__(self, apps):
        self.page_index = 0
        self.apps = apps
        self.pages = self.build_pages()

        super().__init__(
            column_num=10,
            #row_num=3,  # Gets ignored when column is specified
            child=[],
        )

        self.change_page(1)

    def change_page(self, new_page):
        if self.page_index == new_page or new_page > len(self.pages) or new_page < 0:
            return

        self.page_index = new_page
        self.child = self.pages[new_page]

    def build_pages(self):
        pages = dict()
        if not self.apps:
            return pages

        size_apps = len(self.apps)
        full_pages = size_apps // 30  # Returns a 'full page' per 30 apps

        for i in range(1, size_apps+1):
            pages[i] = [AppButton(App(page_app.name, icon_path=page_app.icon_path, exec_cmd=page_app.exec_cmd)) for page_app in self.apps[0+30*i:30+30*i]]


        if size_apps > full_pages * 30:
            last_page_index = full_pages + 1
            pages[last_page_index] = [AppButton(App(page_app.name, icon_path=page_app.icon_path, exec_cmd=page_app.exec_cmd)) for page_app in self.apps[0+30*last_page_index:]]

        return pages
