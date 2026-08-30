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
# This widget shows the systray.
from ignis import widgets
import extra_widgets
from ignis.services.system_tray import SystemTrayItem, SystemTrayService
import asyncio


systray = SystemTrayService.get_default()
 

class trayItem(widgets.Box):
    class trayIcon(widgets.Icon):

        def __init__(self, icon: str | SystemTrayItem.GdkPixbuf.Pixbuf, size: int=50):
            super().__init__(
                pixel_size=size,
                image=icon
            )

    class trayButton(extra_widgets.Button):

        def __init__(self, icon_child, systrayitem: SystemTrayItem, traymenu: SystemTrayItem.menu):
            super().__init__( 
                css_classes = ["sidepanel", "systray", "trayitem", "button"],
                child=icon_child,
                on_click=lambda _: asyncio.create_task(self.activate_self(systrayitem)),
                on_right_click=lambda _: traymenu.popup() if traymenu else None,
                tooltip_text=systrayitem.bind('tooltip'),
            )

        async def activate_self(self, systrayitem):
            try:
                await systrayitem.activate_async() 
            except Exception as e:
                raise(e)

    def __init__(self, trayitem: SystemTrayItem):
        self.id = trayitem.id
        self.category = trayitem.category
        self.title = trayitem.title
        self.tooltip = trayitem.tooltip

        self.tray_menu = trayitem.menu.copy() if trayitem.menu else None

        self.icon = self.trayIcon(trayitem.bind("icon"))
        self.tray_button = self.trayButton(self.icon, trayitem, self.tray_menu)

        super().__init__(
            css_classes = ["sidepanel", "systray", "trayitem"],
            child=[self.tray_button, self.tray_menu],
            #setup=lambda self: trayitem.connect('removed', lambda _: self.unparent()),
            #css_classes = ["sidepanel_widgets", "systray", "background"]
        )
        

class trayGrid(widgets.Grid):

    def __init__(self):
        
        super().__init__(
            css_classes = ["sidepanel", "systray", "background"],
            child = systray.bind(
                "items",
                lambda sysitems: [trayItem(sysitem) for sysitem in sysitems]
            ),
            #setup=lambda self: systray.connect(
            #    "added",
            #    lambda _, sysitem: self.attach_next_to(
            #        child=trayItem(sysitem),
            #        side=1,
            #        width=1,
            #        height=1
            #    )
            #),
            column_num=5,
            column_spacing=6,
            row_spacing=10
        )        
