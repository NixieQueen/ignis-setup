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
# This file reads the contents of the config file provided in its directory and stores it
#

# Unit conversion "true" -> True & 1 -> "1"... etc
def unit_conversion(unit, to_string: bool=False):
    if to_string:
        return str(unit)

    if unit.isnumeric():
        return int(unit)

    match unit:

        case 'True':
            return True

        case 'False':
            return False

        case _:
            return unit


class Config:

    def __init__(self, path):
        self.config = dict()
        self._config_name = f"{path}/utils/config"
        self._config_template = f"{self._config_name}.template"
        
        self.read_config()

    def filter_config_line(self, line: str):
        # Ignore all blank spaces and comments
        if line == '' or line[0] == '#':
            return

        splitline = line.split(': ')
        self.config[splitline[0]] = unit_conversion(splitline[1])

    def assign_value(self, index: str, value: str):
        if not index or not value:
            return
        self.config[index] = value

    def read_config(self):  # Take *every* line as it is, no filters
        with open(self._config_name) as configFile:
            for line in configFile:
                line = line.rstrip('\n')
                self.filter_config_line(line)

    def write_config(self):
        if not self.config:
            return

        with open(self._config_name, "w") as config_file:
            config_file.write('')

        config_file = open(self._config_name, "a")
        with open(self._config_template, "r") as template:
            for line in template:               
                if line == '\n' or line[0] == '#':
                    config_file.write(line)
                    continue

                config_entry = line.split(": ")[0]
                if config_entry in self.config.keys():
                    config_file.write(f"{config_entry}: {self.config[config_entry]}\n")
        config_file.close()
