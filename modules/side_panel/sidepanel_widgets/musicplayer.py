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
# A music player widget with full controls!
from typing import Callable

from ignis import widgets
import extra_widgets
import asyncio
from ignis import utils

from ignis.services.mpris import MprisPlayer
from services.musicservice import MusicService

musicservice = MusicService.get_default()


def seconds_to_minute_format(time: int) -> str:
    if time < 0:
        return "0:00"

    minutes = time // 60
    seconds = time % 60
    seconds = "0" + str(seconds) if seconds < 10 else str(seconds)
    return f"{minutes}:{seconds}"
    
   
class MusicPlayer(widgets.Box):

    class CD(widgets.Overlay):

        def  __init__(self, size: int=160) -> None:
            # Immutable
            self._revolutions = 80

            # Mutable
            self._rotation_step = 1
            self._current_track_length = 0
            self._current_artwork = ""

            # Widgets
            self._disc = extra_widgets.CircleImage(image="media-playback-stop", width=size, height=size, id=0)

            self._dot = widgets.FixedChild(
                widgets.Box(css_classes=["centerdot"], child=[]),
                x=size//2-25, y=size//2-25
            )

            super().__init__(
                css_classes = ["CD"],
                child=self._disc,
                overlays=[
                    widgets.Fixed(
                        child=[self._dot]
                    )
                ]
            )

        def set_rotation_step(self, track_length: int) -> None:
            if track_length == self._current_track_length or not track_length:
                return

            self._current_track_length = track_length
            self._rotation_step = (360 * self._revolutions) // track_length
            self.set_rotation()

        def set_rotation(self, position: float=0) -> None:
            rotation_degrees = position * self._rotation_step
            self._disc.style = f"transform: rotate({rotation_degrees:1.1f}deg);"

        def set_artwork(self, artwork_path: str | None) -> None:
            if self._current_artwork == artwork_path or not artwork_path:
                return

            self._current_artwork = artwork_path
            self._disc.set_cropped_image(artwork_path)

            
    class SeekBar(widgets.Box):

        class SeekLabel(widgets.Label):

            def __init__(self, label: str="", justify: str="") -> None:
                self._current_value = 0
                super().__init__(
                    label=label,
                    justify=justify,
                    wrap=False
                )

            def update_content(self, value: int):
                if value == self._current_value:
                    return
                
                self._current_value = value
                self.label = seconds_to_minute_format(value)

                
        def __init__(self):            
            self._scale = widgets.Scale(
                css_classes=["slider"],
                vertical=False,
                min=0,
                max=1,
                step=1,
                value=0,
                on_change=lambda x: self.__on_change(x.value),
                draw_value=False
            )
            self._current_position = self.SeekLabel(
                label="00:00",
                justify='left',
            )
            self._max_position = self.SeekLabel(
                label="99:99",
                justify='right',
            )

            super().__init__(
                css_classes=["seeker"],
                vertical=True,
                child=[
                    self._scale,
                    widgets.CenterBox(
                        css_classes=["position_text"],
                        start_widget=widgets.Box(child=[self._current_position]),
                        center_widget=widgets.Box(),
                        end_widget=widgets.Box(child=[self._max_position])
                    )
                ]
            )

        def __on_change(self, position: float):
            if not musicservice._player:
                return

            if not musicservice._player.can_seek:
                return
            
            position = int(position)  # Seeker only works in whole numbers
            asyncio.create_task(musicservice._player.set_position_async(position))

        def set_position(self, position: float):
            if self._scale.value == position:
                return
            
            self._scale.value = position
            self._current_position.update_content(int(position))

        
        def set_length(self, track_length: int):
            if not track_length:
                return

            self._scale.max = track_length
            self._max_position.update_content(track_length)
            self.set_position(0)
            
    class TrackInfo(widgets.Box):

        def __init__(self):
            self._title = widgets.Label(
                css_classes=['title'],
                label="title",
                justify="left",
                ellipsize='end',
                max_width_chars=15,
        
            )
            self._artist = widgets.Label(
                css_classes=["subtitle"],
                label="By Artist",
                justify="left",
                ellipsize='end',
                max_width_chars=13
            )
            self._player_id = widgets.Label(
                css_classes=["subtitle"],
                label="On id",
                justify="right",
                ellipsize='end',
                max_width_chars=11
            )

            super().__init__(
                vertical=True,
                css_classes=["trackinfo"],
                child=[
                    self._title,
                    widgets.CenterBox(
                        start_widget = widgets.Box(child=[self._artist]),
                        center_widget = widgets.Box(),
                        end_widget = widgets.Box(child=[self._player_id]),
                    )
                ]
            )

        def set_content(self, title: str, artist: str, player_id: str):
            self._title.label = f"{title}"
            self._artist.label = f"By {artist}"
            self._player_id.label = f"On {player_id}"
            
    class PlayButtons(widgets.Box):

        def __init__(self, update_content_function: Callable):
            self._update_content_function = update_content_function
            
            self._shuffle_status = True
            self._play_pause_status = "Paused"
            self._repeat_status = "Playlist"

            self._previous_button = extra_widgets.IconButton(
                icon='media-skip-backward-symbolic',
                css_classes=['mediabutton'],
                on_click=lambda _: self.previous(),
                pixel_size=28
            )
            
            self._seek_back_button = extra_widgets.IconButton(
                icon='media-seek-backward-symbolic',
                css_classes=['mediabutton'],
                on_click=lambda _: self.seek(-10),
                pixel_size=32
            )

            self._shuffle_button = extra_widgets.IconButton(
                icon='media-playlist-shuffle-symbolic',
                css_classes=['mediabutton'],
                pixel_size=36,
            )

            self._play_pause_button = extra_widgets.IconButton(
                icon='media-playback-start-symbolic',
                css_classes=['mediabutton'],
                on_click=lambda _: self.play_pause(),
                pixel_size=40
            )

            self._loop_button = extra_widgets.IconButton(
                icon='media-playlist-repeat-symbolic',
                css_classes=['mediabutton'],
                pixel_size=36,
            )
                        
            self._seek_forward_button = extra_widgets.IconButton(
                icon='media-seek-forward-symbolic',
                css_classes=['mediabutton'],
                on_click=lambda _: self.seek(10),
                pixel_size=32
            )

            self._next_button = extra_widgets.IconButton(
                icon='media-skip-forward-symbolic',
                css_classes=['mediabutton'],
                on_click=lambda _: self.next(),
                pixel_size=28
            )

            super().__init__(
                css_classes=['buttons'],
                vertical=False,
                homogeneous=True,
                hexpand=True,
                vexpand=False,
                spacing=0,
                child=[
                    self._previous_button,
                    self._seek_back_button,
                    self._shuffle_button,
                    self._play_pause_button,
                    self._loop_button,
                    self._seek_forward_button,
                    self._next_button
                ]
            )

        def set_content(self):
            if not musicservice._player:
                return
            
            self.__on_loop_icon()
            self.__on_play_icon()
            self.__on_shuffle_icon()

            self._previous_button.toggle_disabled(not musicservice._player.can_go_previous)
            self._next_button.toggle_disabled(not musicservice._player.can_go_next)
            self._seek_back_button.toggle_disabled(not musicservice._player.can_seek)
            self._seek_forward_button.toggle_disabled(not musicservice._player.can_seek)

        def __on_play_icon(self):
            if musicservice._player.playback_status == self._play_pause_status:
                return
            
            self._play_pause_button.toggle_disabled(not musicservice._player.can_play)
            
            match musicservice._player.playback_status:
                case "Paused":
                    self._play_pause_button.icon.image = 'media-playback-start-symbolic'
                case "Playing":
                    self._play_pause_button.icon.image = 'media-playback-pause-symbolic'
            self._play_pause_status = musicservice._player.playback_status

        def __on_shuffle_icon(self):
            if musicservice._player.shuffle == self._shuffle_status:
                return
            
            self._shuffle_button.toggle_disabled(not musicservice._player.can_control)

            if musicservice._player.shuffle:
                self._shuffle_button.icon.image = 'media-playlist-shuffle-symbolic'
            else:
                self._shuffle_button.icon.image = 'media-playlist-consecutive-symbolic'
            self._shuffle_status = musicservice._player.shuffle

        def __on_loop_icon(self):
            if musicservice._player.loop_status == self._repeat_status:
                return
            
            self._loop_button.toggle_disabled(not musicservice._player.can_control)
        
            match musicservice._player.loop_status:
                case "Playlist":
                    self._loop_button.icon.image = 'media-playlist-repeat-symbolic'
                case "Track":
                    self._loop_button.icon.image = 'media-playlist-repeat-song-symbolic'
                case "None":
                    self._loop_button.toggle_disabled(True)
            self._repeat_status = musicservice._player.loop_status
                    
        def seek(self, offset: int):
            if not musicservice._player:
                return
            
            if not musicservice._player.can_seek:
                return

            self._update_content_function()

            asyncio.create_task(musicservice._player.seek_async(offset))

        def play_pause(self):
            if not musicservice._player:
                return
            
            if not musicservice._player.can_play:
                return

            self._update_content_function()

            asyncio.create_task(musicservice._player.play_pause_async())
            self.__on_play_icon()

        def previous(self):
            if not musicservice._player:
                return
        
            if not musicservice._player.can_go_previous:
                return

            self._update_content_function()

            asyncio.create_task(musicservice._player.previous_async())

        def next(self):
            if not musicservice._player:
                return
            
            if not musicservice._player.can_go_next:
                return

            self._update_content_function()

            asyncio.create_task(musicservice._player.next_async())
               
            
    def __init__(self):
        # Widgets
        self._CD = self.CD()
        self._seeker = self.SeekBar()
        self._track_info = self.TrackInfo()
        self._play_buttons = self.PlayButtons(lambda: self.assign_content())

        musicservice.bind('signal::assign_content', lambda: self.assign_content())
        musicservice.bind('signal::__on_position_change', lambda _: self.__on_position_change())
        musicservice.bind('signal::__on_animation_change', lambda x: self.__on_animation_change(x))
        
        super().__init__(
            homogeneous=False,
            hexpand=False,
            vexpand=False,
            css_classes=["sidepanel", "musicplayer"],
            spacing=15,
            child=[
                widgets.CenterBox(
                    vertical=True,
                    start_widget=widgets.Box(),
                    center_widget=widgets.Box(child=[self._CD]),
                    end_widget=widgets.Box()
                ),
                widgets.Box(
                    vertical=True,
                    child=[
                        self._track_info,
                        self._seeker,
                        self._play_buttons
                    ]
                )
            ]
        )
                
    def assign_content(self):
        if not musicservice._player:
            return
        
        self._CD.set_artwork(musicservice._player.art_url)
        self._CD.set_rotation_step(musicservice._player.length)
        self._seeker.set_length(musicservice._player.length)
        self._track_info.set_content(
            musicservice._player.title,
            musicservice._player.artist,
            musicservice._player.identity
        )
        self._play_buttons.set_content()
        
    def __on_position_change(self):
        self._play_buttons.set_content()

    def __on_animation_change(self, position: float):
        self._CD.set_rotation(position)
        self._seeker.set_position(position)
