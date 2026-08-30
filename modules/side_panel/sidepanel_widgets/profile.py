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
# This widget shows the profile picture and name of the logged in user.
from ignis import widgets as Widget
from ignis import variable
from ignis import utils
import random
import asyncio

import extra_widgets
#self.desktop_files.desktop_files.connect("notify::value", lambda x, _: self.update_pages(x.value))


class profileText(Widget.Fixed):
    class profileName(Widget.Label):
        
        def __init__(self, profile_name: variable.Variable):
            profile_name.connect("notify::value", lambda x, _: self.assign_username(x.value))
            super().__init__(
                label=profile_name.value,
                justify='center',
                ellipsize='end',
                max_width_chars=7,
                css_classes = ["sidepanel", "profilebanner", "text", "profiletext"]
            )
        def assign_username(self, username):
            self.label = username

            
    class profileFlavour(Widget.Label):
        
        def __init__(self, flavour_text: str=""):
            flavour_texts = [
                "Hello~",
                "Hiii!",
                "Hewwo :3c",
                "Greetings",
                "uwu",
            ]
            self.flavour_text = flavour_text if flavour_text else random.choice(flavour_texts)

            super().__init__(
                label=self.flavour_text,
                justify='center',
                ellipsize='end',
                max_width_chars=12,
                css_classes = ["sidepanel", "profilebanner", "text", "profileflavour"]
            )

    def __init__(self, profile_name: variable.Variable, flavour_text: str=""):
        self.profile_name = self.profileName(profile_name=profile_name)
        self.flavour_text = self.profileFlavour(flavour_text=flavour_text)

        super().__init__(
            child=[
                Widget.FixedChild(
                    widget=self.profile_name,
                    x=0,
                    y=10,
                ),
                Widget.FixedChild(
                    widget=self.flavour_text,
                    x=100,
                    y=70,
                )
            ]
        )

        
class profilePictureWrapped(Widget.Box): 
    class profilePicture(extra_widgets.CircleImage):
     
        def __init__(self, username: variable.Variable, size: int):
            self.size = size

            username.connect("notify::value", lambda x, _: self.assign_username(x.value))
        
            super().__init__(
                image=f"{utils.get_current_dir()}/../../../users/{username.value}.png",
                width=size,
                height=size,
                id=1,
                content_fit="scale_down",
            )

        def assign_username(self, username):
            self.set_cropped_image(f"{utils.get_current_dir()}/../../../users/{username}.png")

            
    def __init__(self, username: variable.Variable, size: int=150):
        self.picture = self.profilePicture(username, size)

        super().__init__(
            css_classes = ["sidepanel", "profilebanner", "profilepicturewrapper"],
            child=[self.picture]
        )


class profileBackground(Widget.Box):

    def __init__(self):
        super().__init__(
            css_classes = ["sidepanel", "profilebanner", "background"]
        )


class profileBanner(Widget.CenterBox):

    def __init__(self):
        self.username = variable.Variable(value="default")

        asyncio.create_task(self.assign_username())

        self.profile_picture = profilePictureWrapped(self.username)
        self.profile_text_wrapped = profileText(self.username)

        self.picture_text_box = Widget.Box(
            #spacing = 12,
            child=[
                self.profile_picture,
                self.profile_text_wrapped
            ]
        )
        
        super().__init__(
            css_classes = ["sidepanel", "profilebanner", "background"],
            start_widget=Widget.Box(),
            center_widget=Widget.Box(
                child=[self.picture_text_box],
            ),
            end_widget=Widget.Box()
        )
        
    async def assign_username(self):
        username_cmd = await utils.exec_sh_async(command='whoami')
        self.username.value = username_cmd.stdout.rstrip('\n')
        
