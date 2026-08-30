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
# A service for polling and updating music players
from ignis import utils
from .baseservice import BaseService
import asyncio
import extra_widgets
from ignis.services.mpris import MprisService, MprisPlayer

mpris = MprisService.get_default()


def get_priority_stream() -> MprisPlayer | None:
    priority_list = ["Spotify", "VLC media player"]
    identities = [player.identity for player in mpris.players]
    for priority in priority_list:
        if priority in identities:
            return mpris.players[identities.index(priority)]
    
    return mpris.players[0]


class MusicService(BaseService):

    def __init__(self):
        self._poll = None
        self._player = None
        self._current_position = 0
        self._title = ""
        self._position_animator = extra_widgets.animationVariable(value=0, method="linear", time=3, step_size=0.025)

        super().__init__(
            signals=[
                "signal::assign_content",
                "signal::__on_position_change",
                "signal::__on_animation_change"
            ]
        )
        
        # Signals
        self._position_animator.connect('notify::value', lambda x, _: self.__on_animation_change(x.value))
        mpris.connect('player_added', lambda _, x: self.__on_player_added())

    def __on_player_added(self):
        player = get_priority_stream()
        if not player:
            return
        
        if self._player == player:
            return

        self._player = player

        if self._poll:
            self._poll.cancel()
        self._poll = utils.Poll(timeout=3_000, callback=lambda _: self.__on_position_change(self._player.position))

        '''
        Set any content to widgets
        '''
        # Do signalling here!
        # Assign content
        self.emit('signal::assign_content')
    
        '''
        Update any widgets and context related to the song/player!
        '''
        #self._player.bind('position', lambda x: self.__on_position_change(x))
        self._player.connect('closed', lambda _: self.__on_player_closed())
        #self._play_buttons.on_signal()

    def __on_notification(self):
        if not self._player:
            return
        
        asyncio.create_task(utils.exec_sh_async(f"notify-send -i {self._player.art_url} 'Now playing' '{self._player.title} by {self._player.artist}'"))
        
    def __on_player_closed(self):
        if not mpris.players:
            self._player = None
            self.__on_position_change(0)

            if self._poll:
                self._poll.cancel()
            self._poll = None
        else:
            self.__on_player_added()

    def __on_position_change(self, position: int):
        self.emit('signal::__on_position_change', position)
        if position == self._current_position:
            return

        if not self._player:
            return

        self._current_position = position
        self._position_animator.target.value = position + 3 if position != 0 else position

        if self._title != str(self._player.title):
            self._title = str(self._player.title)
            self.__on_notification()
            self.emit('signal::assign_content')
            

    def __on_animation_change(self, position: float):
        pass
        self.emit('signal::__on_animation_change', position)

