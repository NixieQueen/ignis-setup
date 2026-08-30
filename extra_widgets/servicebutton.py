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
import extra_widgets
from ignis import utils as Utils


class ServiceRevealer(widgets.Revealer):

    def __init__(self, info_child, transition_type: str="slide_left", transition_duration: int=500):
        super().__init__(
            visible=False,
            child=info_child,
            transition_type=transition_type,
            transition_duration=transition_duration,
            reveal_child=True,
        )
        self.set_reveal_child(False)

    @Utils.debounce(200)
    def show_revealer(self):      
        self.visible = True
        self.set_reveal_child(True)
       
    #@Utils.debounce(1000)
    def hide_revealer(self):
        Utils.Timeout(
            ms=self.transition_duration,
            target=lambda self=self: self.set_visible(False)
        )
        self.set_reveal_child(False) 


class ServiceButton(extra_widgets.Button):

    def __init__(self, child, on_click):
        super().__init__(
            child=child or [],
            on_click=on_click,
            css_classes=['toppanel_button']
        )
        

class ServiceHover(widgets.EventBox):

    def __init__(self, icon_image, info_child, on_click, pixel_size: int=26):
        icon = widgets.Icon(image=icon_image, pixel_size=pixel_size)

        self.service_button = ServiceButton(child=icon, on_click=on_click)
        service_revealer = ServiceRevealer(info_child)
        
        super().__init__(
            child=[service_revealer, self.service_button],
            spacing=6,
            css_classes=['toppanel_service'],
            on_hover=lambda _: service_revealer.show_revealer(),
            on_hover_lost=lambda _: service_revealer.hide_revealer()
        )


class TaskbarHover(widgets.EventBox):

    def __init__(self, info_child):
        self._taskbar_wrapper = widgets.Box(
            child=[info_child],
            css_classes=["taskbar"],
            style="border-radius: 2rem 2rem 0rem 0rem; margin: 0rem;"
        )
        self._service_revealer = ServiceRevealer(self._taskbar_wrapper, transition_type="slide_up")
        self._taskbar_hover_point = widgets.Box(child=[], css_classes=['taskbar_hover'])

        super().__init__(
            child=[
                self._taskbar_hover_point,
                self._service_revealer
            ],
            vertical=True,
            #spacing=6,
            css_classes=['taskbar_hover'],
            on_hover=lambda _: self._service_revealer.show_revealer(),
            on_hover_lost=lambda _: self._service_revealer.hide_revealer()
        )
