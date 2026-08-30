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
# Managing the Niri config by writing smaller files and merging it into
# a larger "config.kdl" file
#
from ignis import utils as Utils


class  NiriConfigManager:

    def __init__(self, home_dir: str) -> None:
        self._niri_path = home_dir + "/.config/niri/"
        self._header_line = "// Config written by ignis niri manager script!\n"

        self._blur_config = f"{self._niri_path}blur.kdl"
        self._monitor_config = f"{self._niri_path}monitors.kdl"
        
        self._sub_configs = [f"{self._niri_path}main.kdl", self._blur_config, self._monitor_config]
        self._final_config = f"{self._niri_path}config.kdl"

        self._config = {}
        self.assign_config_value('blur', self.read_blur_config())

    def assign_config_value(self, index: str, value: str | int | float | bool | None):
        if not index:
            return

        self._config[index] = value

    def merge(self) -> None:
        sub_configs = " ".join(self._sub_configs)
        Utils.exec_sh(f"cat {sub_configs} > {self._final_config}")

    def write_monitor_config(self, monitor_config: list) -> None:
        '''
        dict is made up of name, on/off, mode (resolution@refresh_rate),
        scale, rotation and position

        'name': str 
        'status': bool
        'mode': str ([x]x[y]@[z])
        'scale': str (float 1.1)
        'rotation': str (normal, 90, 180, 270, flipped, flipped-90, flipped-180, flipped-270)
        'posx': str (int)
        'posy': str (int)
        '''
        if not monitor_config:
            return
        
        with open(self._monitor_config, "w") as monitor_file:
            monitor_file.write(self._header_line)

        with open(self._monitor_config, "a") as monitor_file:
            for monitor in monitor_config:
                monitor_file.write(f'output "{monitor["name"]}" ' + "{\n")
                if not monitor['status']:
                    monitor_file.write(f"\toff\n")
                monitor_file.write(f'\tmode "{monitor["mode"]}"\n')
                monitor_file.write(f'\tscale {monitor["scale"]}\n')
                monitor_file.write(f'\ttransform "{monitor["rotation"]}"\n')
                monitor_file.write(f'\tposition x={monitor["posx"]} y={monitor["posy"]}\n')
                monitor_file.write("}\n\n")

    def read_blur_config(self):
        blur = None
        with open(self._blur_config, "r") as blur_file:
            for line in blur_file:
                if not ("blur" in line) or line[0] == "/":
                    continue
                
                line = line.rstrip('\n')
                match line.split('r ')[1]:
                    case 'true':
                        blur = True
                    case 'false':
                        blur = False
                    case _:
                        blur = False
                break
        return blur    
                
    def write_blur_config(self):
        blur_str = str(self._config['blur']).lower()
        print('\n\n\n' + blur_str)
        with open(self._blur_config, "w") as blur_file:
            blur_file.write(self._header_line)

        with open(self._blur_config, "a") as blur_file:
            blur_file.write('// Enable blur behind the ignis client.\nlayer-rule {\n\tmatch namespace="ignis"\n\n\t background-effect {\n')
            blur_file.write(f'\t\tblur {blur_str}\n\t\txray false\n')
            blur_file.write("\t}\n}\n")
        
