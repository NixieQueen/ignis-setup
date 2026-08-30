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
from ignis import utils, widgets
from ignis.variable import Variable
from ignis.window_manager import WindowManager
import extra_widgets


windowmanager = WindowManager.get_default()


class Timer(widgets.Box):

    def __init__(self, timer_variable):
        self.timer = widgets.Label(
            label=f"{timer_variable.value}",
            justify="center",
            max_width_chars=3,
            css_classes=["timerfont"]
        )
        timer_variable.connect("notify::value", lambda x, _: self.timer.set_property('label',f"{x.value}"))

        self.subtext = widgets.Label(
            label="Seconds until shutdown",
            justify="center",
            css_classes=["subfont"]
        )
        super().__init__(
            vertical=True,
            css_classes=["quitmenu", "timer"],
            child=[
                self.timer,
                self.subtext
            ]
        )


class Buttons(widgets.Box):
    class ShutdownButton(extra_widgets.Button):

        def __init__(self, icon_image: str="", onclick=None, pixel_size: int=40):
            icon = widgets.Icon(image=icon_image, pixel_size=pixel_size)

            super().__init__(
                css_classes=["button"],
                child=icon,
                on_click=onclick
            )

    def __init__(self, cancelaction, rebootaction, shutdownaction):
        self.cancel_button = self.ShutdownButton(
            "window-close-symbolic",
            cancelaction
        )
        self.reboot_button = self.ShutdownButton(
            "system-reboot-symbolic",
            rebootaction
        )
        self.shutdown_button = self.ShutdownButton(
            "system-shutdown-symbolic",
            shutdownaction
        )


        super().__init__(
            vertical=False,
            homogeneous=True,
            css_classes=["quitmenu", "buttons"],
            child=[
                self.cancel_button,
                self.reboot_button,
                self.shutdown_button
            ]
        )
        

class Clock(widgets.Box):

    def __init__(self, timeout: int=60):
        self.start_timeout = timeout
        self.timeout = Variable(value=timeout)

        self.poll = False

        super().__init__(
            vertical=True,
            css_classes=["quitmenu"],
            child=[
                Timer(self.timeout),
                Buttons(
                    lambda _: self.end_timer(),
                    lambda _: utils.exec_sh("reboot"),
                    lambda _: utils.exec_sh("shutdown now")
                )
            ]
        )

    def tick_timer(self):
        if not self.poll:
            return
        
        utils.Timeout(ms=1000, target=lambda: self.tick_timer())
            
        if self.timeout.value <= 0:
            self.end_timer()
            utils.exec_sh("shutdown now")
            return
            
        self.timeout.value = self.timeout.value - 1
        
    def start_timer(self):
        if self.poll:
            return

        self.timeout.value = self.start_timeout
        self.poll = True
        utils.Timeout(ms=1000, target=lambda: self.tick_timer())
        
    def end_timer(self):
        if not self.poll:
            return

        self.poll = False
        windowmanager.close_window("ignis_quitmenu")
    
