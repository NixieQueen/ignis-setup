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
# Basically all takes from github.com/linkfrg/dotfiles
# ( Sorry, I got quite lazy here 3: )
#
from ignis import widgets
from ignis import utils
from ignis.services.notifications import Notification, NotificationService
from extra_widgets import NotificationWidget

from services import ScreennameToId
from ignis.services.niri import NiriService


way_wm = NiriService.get_default()
screenname = ScreennameToId.get_default()
notifications = NotificationService.get_default()


class Popup(widgets.Box):
    def __init__(
        self, box: "PopupBox", window: "notification_popup", notification: Notification
    ):
        self._box = box
        self._window = window

        widget = NotificationWidget(notification)
        widget.css_classes = ["notification-popup"]
        self._inner = widgets.Revealer(transition_type="slide_down", child=widget)
        self._outer = widgets.Revealer(transition_type="slide_up", child=self._inner)
        super().__init__(child=[self._outer], halign="end")

        notification.connect("dismissed", lambda x: self.destroy())

    def destroy(self):
        def box_destroy():
            self.unparent()
            if len(notifications.popups) == 0:
                self._window.visible = False

        def outer_close():
            self._outer.reveal_child = False
            utils.Timeout(self._outer.transition_duration, box_destroy)

        self._inner.transition_type = "crossfade"
        self._inner.reveal_child = False
        utils.Timeout(self._outer.transition_duration, outer_close)


class PopupBox(widgets.Box):
    def __init__(self, window: "notification_popup", monitor_id: int):
        self._window = window
        self._monitor = monitor_id

        super().__init__(
            vertical=True,
            valign="start",
            setup=lambda self: notifications.connect(
                "new_popup",
                lambda x, notification: self.__on_notified(notification),
            ),
        )

    def __on_notified(self, notification: Notification) -> None:
        if not (self._monitor == screenname.name_to_id(way_wm.active_output)):
            return

        self._window.visible = True
        popup = Popup(box=self, window=self._window, notification=notification)
        self.prepend(popup)
        popup._outer.reveal_child = True
        utils.Timeout(
            popup._outer.transition_duration, popup._inner.set_reveal_child, True
        )


class notification_popup(widgets.Window):
    def __init__(self, monitor_id: int):
        super().__init__(
            anchor=["top"],
            monitor=monitor_id,
            namespace=f"ignis_notification_{monitor_id}",
            layer="overlay",
            child=PopupBox(window=self, monitor_id=monitor_id),
            visible=False,
            dynamic_input_region=False,
            #css_classes=["rec-unset"],
            style="min-width: 29rem;",
        )
