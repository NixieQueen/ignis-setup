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
def unit_conversion(unit, to_string=False):
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
        self.configName = f"{path}/utils/config"

        self.full_config = list()

        self.read_config()

    def filter_config_line(self, line):
        # Ignore all blank spaces and comments
        if line == '' or line[0] == '#':
            return

        line = line.split(': ')
        self.config[line[0]] = unit_conversion(line[1])

    def read_config(self):  # Take *every* line as it is, no filters
        self.full_config = list()
        with open(self.configName) as configFile:
            for line in configFile:
                line = line.rstrip('\n')
                self.full_config.append(line)
                self.filter_config_line(line)

    def write_config(self):
        if not self.config or not self.full_config:
            self.read_config()

        with open(self.configName, "w") as configFile:
            configFile.write('')

        with open(self.configName, "a") as configFile:
            for line in self.full_config:
                # Find config entries and change if needed
                config_entry = line.split(": ")[0]
                if config_entry in self.config.keys():
                    if not line.split(": ")[1] == self.config[config_entry]:
                        line = f"{config_entry}: {self.config[config_entry]}"


                configFile.write(f"{line}\n")
