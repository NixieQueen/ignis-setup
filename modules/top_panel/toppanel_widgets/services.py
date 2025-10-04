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
#
# Creates buttons for services on the top panel
# : Audio
# : Power
# : Network
# : Bluetooth
#
from ignis import widgets as Widget
from ignis.services.audio import AudioService
from ignis.services.upower import UPowerService
from ignis.services.network import NetworkService
from ignis.services.bluetooth import BluetoothService
from ignis import utils as Utils

Audio = AudioService.get_default()
Power = UPowerService.get_default()
Network = NetworkService.get_default()
Bluetooth = BluetoothService.get_default()


class ServiceRevealer(Widget.Revealer):

    def __init__(self, info_child):
        super().__init__(
            visible=False,
            child=info_child,
            transition_type='slide_right',
            transition_duration=500,
            reveal_child=True
        )
        self.set_reveal_child(False)

    def change_visible(self, visible):
        if visible:
            self.visible = visible
            self.set_reveal_child(visible)
            return
       
        Utils.Timeout(
            ms=self.transition_duration//2,
            target=lambda self=self: self.set_visible(visible)
        )
        self.set_reveal_child(visible)


class ServiceButton(Widget.Button):

    def __init__(self, child, on_click):
        super().__init__(
            child=child or [],
            on_click=on_click,
            css_classes=['toppanel_button']
        )
        

class ServiceHover(Widget.EventBox):

    def __init__(self, icon_image, info_child, on_click):
        icon = Widget.Icon(image=icon_image, pixel_size=26)

        service_button = ServiceButton(child=icon, on_click=on_click)
        service_revealer = ServiceRevealer(info_child)
        
        super().__init__(
            child=[service_button, service_revealer],
            spacing=6,
            css_classes=['toppanel_service'],
            on_hover=lambda _: service_revealer.change_visible(True),
            on_hover_lost=lambda _: service_revealer.change_visible(False)
        )


class AudioButton(ServiceHover):

    def __init__(self, speaker: bool=True, max: int=100):
        self.audiodevice = Audio.speaker if speaker else Audio.microphone
        slider = Widget.Scale(
            min=0,
            max=max,
            step=5,
            value=self.audiodevice.bind("volume"),
            on_change=lambda x: self.audiodevice.set_volume(x.value),
            #sensitive=audiodevice.bind("is_muted", lambda value: not value),
            #draw_value=True,
            css_classes=["toppanel_slider"]
        )

        #=audio.speaker.bind("icon_name"),
        #sensitive=x.bind("is_muted", lambda value: not value)
        # Icons:
        # audio-volume-high-symbolic
        # audio-volume-medium-symbolic
        # audio-volume-low-symbolic
        # audio-volume-muted-symbolic
        # microphone-sensitivity?

        missing_prefix = 'audio-volume' if speaker else 'microphone-sensitivity'
        
        super().__init__(
            icon_image=self.audiodevice.bind(
                'icon_name',
                lambda x:
                    f'{missing_prefix}-muted-symbolic' if x == 'image-missing' else x
            ),
            info_child=slider,
            on_click=lambda _: self.toggle_mute()
        )

    def toggle_mute(self):
        if self.audiodevice.id >= 0:
            self.audiodevice.is_muted = not self.audiodevice.is_muted


class PowerButton(ServiceHover):

    def __init__(self, powerdevice):
        # Icons:
        # battery-symbolic
        # empty - caution - low - good - full
        # battery-{}-charging-symbolic
        # battery-{}-symbolic
        #
        slider = Widget.Scale(
            min=0,
            max=100,
            value=powerdevice.bind('percent'),
            sensitive=False,
            #draw_value=True,
            css_classes=["toppanel_slider"]
        )
        label = Widget.Label(
            label=powerdevice.bind('time_remaining', lambda x: str(x))
        )

        super().__init__(
            icon_image=powerdevice.bind('icon_name'),
            info_child=Widget.Box(child=[label, slider]),
            on_click=lambda _: None
        )

    
class WifiButton(ServiceHover):

    def __init__(self):
        # Icons:
        # wired - wireless
        # network-{}-disconnected-symbolic
        # network-{}-symbolic
        # 
        pass


class BluetoothButton(ServiceHover):

    def __init__(self):
        # Icons:
        # bluetooth-active-symbolic
        # bluetooth-disabled-symbolic
        pass
  

class Services(Widget.Box):

    def __init__(self):
        # Add audio and power services
        service_child = [
            AudioButton(speaker=True),
            AudioButton(speaker=False, max=153)  # Max is higher as microphone allows higher maximum amount
        ]

        if Power.devices:
            service_child.append(
                PowerButton(powerdevice=Power.devices[0])
            )

        if Bluetooth.state != 'absent':
            pass
            # Add bluetooth if it is present
            #child.append('')

        if Network.wifi.devices or Network.ethernet.devices:
            pass
            # Add network if it is present
            #child.append('')
        
        super().__init__(
            child=service_child
        )
