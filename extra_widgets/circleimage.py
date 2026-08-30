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
# Circularly cropped image!
from ignis import widgets

import numpy
from PIL import Image, ImageDraw


class CircleImage(widgets.Picture):

    def __init__(self, image: str, width: int, height: int, id: int, *args, **kwargs):
        self._reserved_slot = f"/home/nixie/.cache/ignis/art_url/cropped_circle{id}.png"
        self._height = height
        self._width = width
        
        self._mask = self.create_mask()
        self.create_cropped_image(image)
        
        super().__init__(
            image=self._reserved_slot,
            width=width,
            height=height,
            *args,
            **kwargs
        )

    def create_mask(self):
        mask_image = Image.new('L', [self._height,self._width] , 0)

        draw = ImageDraw.Draw(mask_image)
        draw.pieslice([(0,0), (self._height,self._width)], 0, 360, fill = 255, outline = "white")
        mask_array = numpy.array(mask_image)
        return mask_array

    def write_slot(self, cropped_image):
        cropped_image.save(self._reserved_slot)

    def create_cropped_image(self, new_image_path: str):
        try:
            image = Image.open(new_image_path).convert('RGB')
        except FileNotFoundError:
            return

        width, height = image.size
        if width < self._width or height < self._height:
            image = image.resize((self._width, self._height))
        else:
            if width > height:
                new_width = int(width * (self._height / height))
                image = image.resize((new_width, self._height))
                center_x = new_width // 2
                center_y = self._height // 2
            elif width < height:
                new_height = int(height * (self._width / width))
                image = image.resize((self._width, new_height))
                center_x = self._width // 2
                center_y = new_height // 2
            else:
                image = image.resize((self._width, self._height))
                center_x = self._width // 2
                center_y = self._height // 2
            image = image.crop((center_x-self._width//2, center_y-self._height//2, center_x+self._width//2, center_y+self._height//2))
                
        image_array = numpy.asarray(image)
        #image_array = image_array[...,:3]
        image_array = numpy.dstack((image_array,self._mask))
        image = Image.fromarray(image_array)
        self.write_slot(image)

    def set_cropped_image(self, new_image_path: str):
        self.create_cropped_image(new_image_path)

        self.image = self._reserved_slot
