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
import datetime
import asyncio
from ignis import widgets as Widget
from ignis.services.audio import AudioService
from ignis.services.upower import UPowerService
from ignis.services.network import NetworkService
from ignis.services.bluetooth import BluetoothService
from ignis.services.fetch import FetchService
from extra_widgets.servicebutton import ServiceHover
from ignis import utils as Utils
from ignis.window_manager import WindowManager


Audio = AudioService.get_default()
Power = UPowerService.get_default()
Network = NetworkService.get_default()
Bluetooth = BluetoothService.get_default()

fetch = FetchService.get_default()
window_manager = WindowManager.get_default()


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
            css_classes=['toppanel_font'],
            label=powerdevice.bind('time_remaining', lambda x: str(datetime.timedelta(seconds=x) if x else "???"))
        )

        super().__init__(
            icon_image=powerdevice.bind('icon_name'),
            info_child=Widget.Box(child=[label, slider], spacing=5),
            on_click=lambda _: None
        )

    
class NetworkButton(ServiceHover):

    def __init__(self, networktype):
        self.networktype = networktype
        self.networkdevice = Network.ethernet.devices[0] if networktype == 'ethernet' \
            else Network.wifi.devices[0]
        self.networkparent = Network.ethernet if networktype == 'ethernet' else Network.wifi
        # Icons:
        # wired - wireless
        # network-{}-disconnected-symbolic
        # network-{}-symbolic
        #
        if networktype == 'ethernet':
            label_name = Widget.Label(
                css_classes=['toppanel_font'],
                label=self.networkdevice.bind('name', lambda x: f"'{x}'")
            )
            label_speed = Widget.Label(
                css_classes=['toppanel_font'],
                label=self.networkdevice.bind('speed', lambda x: f"{x}Mhz")
            )
            network_child = Widget.Box(child=[label_name, label_speed], spacing=5)
        else:
            label_name = Widget.Label(
                css_classes=['toppanel_font'],
                label=self.networkdevice.ap.bind('ssid', lambda x: f"'{x}'")
            )
            label_speed = Widget.Label(
                css_classes=['toppanel_font'],
                label=self.networkdevice.ap.bind('strength', lambda x: f"{x}%")
            )
            network_child = Widget.Box(child=[label_name, label_speed], spacing=5)
        
        super().__init__(
            icon_image=self.networkparent.bind('icon_name'),
            info_child=network_child,
            on_click=lambda _: self.toggle_network()
        )

    def toggle_network(self):
        if self.networktype == 'ethernet':
            if self.networkdevice.is_connected:
                asyncio.create_task(self.networkdevice.disconnect_from())
                return
            
            asyncio.create_task(self.networkdevice.connect_to())
            return

        self.networkparent.enabled = not self.networkparent.enabled        


class BluetoothButton(ServiceHover):

    def __init__(self):
        # Icons:
        # bluetooth-active-symbolic
        # bluetooth-disabled-symbolic

        self.label = Widget.Label(
            css_classes=['toppanel_font'],
            label=Bluetooth.bind('connected_devices', lambda x: f"Connections: {len(x)}")
        )
        
        super().__init__(
            icon_image=Bluetooth.bind('powered', lambda power: 'bluetooth-active-symbolic' if power else 'bluetooth-disabled-symbolic'),
            info_child=self.label,
            on_click=lambda _: self.toggle_bluetooth()
        )

    def toggle_bluetooth(self):
        Bluetooth.powered = not Bluetooth.powered
        

class sideButton(ServiceHover):

    def __init__(self, monitor_id: int):
        self.label = Widget.Label(
            label = "Uptime: ",
            css_classes = ['toppanel_font']
        )
        fetch_poll = Utils.Poll(timeout=60000, callback=lambda _: self.update_uptime())

        super().__init__(
            icon_image='view-list-symbolic',
            info_child=self.label,
            on_click=lambda _: window_manager.open_window(f"ignis_sidepanel_{monitor_id}")
        )

    def update_uptime(self):
        fetch_uptime = fetch.uptime or (0, 0, 0, 0)
        self.label.label = f"Uptime: {fetch_uptime[0]} days {fetch_uptime[1]}h{fetch_uptime[2]}m{fetch_uptime[3]}s"

        
class settingsButton(ServiceHover):

    def __init__(self):
        self.label = Widget.Label(
            label = "Settings",
            css_classes = ['toppanel_font']
        )

        super().__init__(
            icon_image='emblem-system-symbolic',
            info_child=self.label,
            on_click=lambda _: window_manager.open_window(f"ignis_settingsmenu")
        )

      
class Services(Widget.Box):

    def __init__(self, monitor_id: int=0):
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
            # Add bluetooth if it is present
            service_child.append(
                BluetoothButton()
            )

        if Network.wifi.devices or Network.ethernet.devices:
            service_child.append(
                NetworkButton(networktype='ethernet' if Network.ethernet.devices else 'wifi')
            )
            # Add network if it is present
        
        service_child.append(settingsButton())
        service_child.append(sideButton(monitor_id))
               
        super().__init__(
            child=service_child,
            css_classes=['toppanel_workspace']
        )
