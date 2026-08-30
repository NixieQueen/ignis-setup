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
# This 'widget' is an ignis Variable with animatable properties
# Its value can be assigned to some widget just like a normal Variable
# However, changing the self.target's value will animate your widget's value
# towards the called target
# This behaviour can be altered using the total animation time, animation method and precision
from ignis.variable import Variable
import time
import asyncio


def easeInOutCubic(t):
    #https://gist.github.com/robweychert/7efa6a5f762207245646b16f29dd6671
    t *= 2
    if t < 1:
        return t * t * t / 2
    else:
        t -= 2
        return (t * t * t + 2) / 2

def linear(t):
    return t

        
class animationVariable(Variable):
    
    def __init__(self, value: float, time: float=0.5, method: str="easeInOutCubic", step_size: float=0.01):
        self.curves = {
            'easeInOutCubic': easeInOutCubic,
            'linear': linear
        }
       
        self.animation_running = False
        self.time = time
        self.method = method
        self.step_size = step_size
        
        self.target = Variable(value=value)
        self.target.connect("notify::value", lambda _, x: asyncio.create_task(self.move_to_target()))
        
        super().__init__(
            value=value
       )

    
    async def move_to_target(self):
        if self.animation_running:
            pass

        await self.run_animation()

        #self.value = self.target.value
        self.animation_running = False
        
    async def run_animation(self):
        self.animation_running = True
        start_point = float(self.value)
        end_point = float(self.target.value)
        delta = end_point - start_point

        ease_function = self.curves[self.method]

        elapsed = 0
        end_time = time.time() + self.time
        while time.time() <= end_time:
            elapsed += self.step_size
            self.value = start_point + delta * ease_function(elapsed / self.time)
            await asyncio.sleep(self.step_size)
