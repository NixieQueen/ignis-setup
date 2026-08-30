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
# This widget can be used to toggle between various performance settings using TLP
# Requires TLP to work!
from ignis import widgets
import extra_widgets
import asyncio
from ignis import variable
from ignis import utils


class PerformanceButton(extra_widgets.Button):

    def __init__(self, text, on_click, mode: variable.Variable):
        self.button_name = text
        self.text = widgets.Label(
            justify="center",
            label=text,
            css_classes=mode.bind('value', lambda x: self.get_css(x))
        )
        
        super().__init__(
            css_classes=['sidepanel','performanceswitch', 'button'],
            child=self.text,
            on_click=on_click,
        )

    def get_css(self, mode):
        css = ['sidepanel', 'performanceswitch', 'text']
        if mode == self.button_name:
            return css
        else:
            return css + ['disabled']
        

class PerformanceSlider(widgets.Scale):

    def __init__(self, mode: variable.Variable):
        mode.connect("notify::value", lambda x, _: self.set_state_slider(x.value))
        self.slider_value = extra_widgets.animationVariable(value=0, time=1)
        super().__init__(
            css_classes=["sidepanel", "performanceswitch", "slider"],
            min=0,
            max=2,
            step=1,
            value=self.slider_value.bind('value', lambda x: x),
            draw_value=False,
            sensitive=False
        )

    def set_state_slider(self, active_profile):
        value = self.get_state_slider(active_profile)
        if self.slider_value.target.value == value:
            return

        self.slider_value.target.value = value

    def get_state_slider(self, active_profile):
        match active_profile:
            case "performance":
                return 0
            case "balanced":
                return 1
            case "power-saver":
                return 2


class PerformanceSwitch(widgets.Box):

    def __init__(self):
        self.mode = variable.Variable(value="performance")
        
        self.buttons = [
            PerformanceButton("performance", lambda _: self.switch_mode('performance'), self.mode),
            PerformanceButton("balanced", lambda _: self.switch_mode('balanced'), self.mode),
            PerformanceButton("power-saver", lambda _: self.switch_mode('power-saver'), self.mode),             
        ]
        self.performance_buttons = widgets.Box(
            homogeneous=True,
            spacing=10,
            child=self.buttons
        )

        self.performance_slider = PerformanceSlider(self.mode)
                
        super().__init__(
            vertical=True,
            css_classes=["sidepanel", "performanceswitch", "background"],
            child=[self.performance_buttons, self.performance_slider]
        )

    def switch_mode(self, mode):
        if self.mode.value == mode:
            return

        asyncio.create_task(utils.exec_sh_async(f'pkexec tlp {mode}'))
        
        self.mode.value = mode
        
            
            
