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
from ignis.services.systemd import SystemdService
import asyncio


systemd_service = SystemdService.get_default()


class Button(widgets.Button):

    def __init__(self, css_classes: list=[], child=None, on_click=None, on_right_click=None, on_middle_click=None, timer_disable: bool=False, default_state: bool=False, *args, **kwargs):
        self.disabled = False
        self.clicked = default_state
        self.css_class = css_classes
        self.timer_disable = timer_disable
        super().__init__(
            css_classes=css_classes,
            child=child,
            on_click=lambda _: self.click_handler(on_click),
            on_right_click=lambda _: self.click_handler(on_right_click),
            on_middle_click=lambda _: self.click_handler(on_middle_click),
            *args,
            **kwargs
        )
        if self.clicked:
            self.add_css_class("clicked")

    def click_handler(self, click_function):
        self.clicked = not self.clicked
        if self.clicked:
            self.add_css_class("clicked")
        else:
            self.remove_css_class("clicked")
        if click_function:
            click_function(self)
        if not self.timer_disable:
            asyncio.create_task(self.turn_off())
        
    async def turn_off(self):
        await asyncio.sleep(.200)
        self.remove_css_class("clicked")

    def toggle_disabled(self, disabled: bool | None=None):
        if disabled == self.disabled:
            return
        
        if disabled == None:
            disabled = not self.disabled
            
        self.disabled = disabled
        if disabled:
            self.add_css_class('disabled')
        else:
            self.remove_css_class('disabled')


class TextButton(Button):

    def __init__(
            self,
            text: str | None,
            css_classes: list=[],
            on_click=None,
            on_right_click=None,
            on_middle_click=None,
            timer_disable: bool=False,
            *args, **kwargs
    ):
        self._text = widgets.Label(label=text, justify="center", wrap=False)
        super().__init__(
            css_classes=css_classes,
            child=self._text,
            on_click=on_click,
            on_right_click=on_right_click,
            on_middle_click=on_middle_click,
            timer_disable=timer_disable,
            *args,
            **kwargs
        )
        

class IconButton(Button):

    def __init__(
            self,
            icon: str | None,
            css_classes: list=[],
            on_click=None,
            on_right_click=None,
            on_middle_click=None,
            timer_disable: bool=False,
            pixel_size: int=32,
            default_state: bool=False,
            *args, **kwargs
    ):
        self.icon = widgets.Icon(image=icon, pixel_size=pixel_size)
        super().__init__(
            css_classes=css_classes,
            child=self.icon,
            on_click=on_click,
            on_right_click=on_right_click,
            on_middle_click=on_middle_click,
            timer_disable=timer_disable,
            default_state=default_state,
            *args,
            **kwargs
        )


class SysServiceButton(IconButton):
    def __init__(
            self,
            service: str,
            icon: str | None,
            css_classes: list=[],
            timer_disable: bool=False,
            pixel_size: int=32,
            *args, **kwargs
    ):
        self.service_unit = systemd_service.get_unit(service)
        super().__init__(
            icon=icon,
            css_classes=self.service_unit.bind(
                'is_active',
                lambda x: css_classes if x else css_classes + ['disabled']
            ),
            on_click=lambda _: self.toggle_service(),
            timer_disable=timer_disable,
            pixel_size=pixel_size,
            *args,
            **kwargs
        )

    def toggle_service(self):
        if self.service_unit.is_active:
            asyncio.create_task(self.service_unit.stop_async())
            return

        asyncio.create_task(self.service_unit.start_async())
