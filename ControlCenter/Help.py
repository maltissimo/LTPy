from Hardware import obis_commands
import inspect

class GantryHelp():
    """
    A class displaying some generics about the Gantry movements.
    """
    def __init__(self):
        pass
    def Gantry_generic(self):
        """
        A little helping function printing out all the motors, how they move, and their units.
        :return:
         X = 5,     Coordinate System:  3, units: microns
         Y = 6,     Coordinate system: 3 units: microns
         Z = Z,     Coordinate system: 1, moves the RTT stage up and down, units: microns
        Roll = A,  Coordinate System: 1, tips the RTT stage towards front or back, i.e. rotation around X axis, units: degrees
        Pitch = B, Coordinate System: 1, tilts the RTT stage towards left and right, i.e. Rotation around Y axis, units: degrees
         Rot = C,   Coordinate System: 2, rotation around Z axis, units: degrees

        """
        text = "\n"
        text += "            PMAC Name   QSYS Name      Coord. System   Units               Movement "
        text += "\n"
        text += "   X           5          5             3               µm                 Horizontal "
        text += "\n"
        text += "   Y           6          6             3               µm                Front-Back"
        text += "\n"
        text += "   Z           Z        1+2+3           1               µm                 RTT up/down"
        text += "\n"
        text += " Roll          A        1+2+3           1             degrees      X rot, tips RTT front/back"
        text += "\n"
        text += " Pitch         B        1+2+3           1             degrees      Y rot, tilts RTT left/right"
        text += "\n"
        text += " Yaw           C          4             2                 degrees      Z rot, RTT around its axis"
        return(text)
=
    def Motor(self):

        text ="\n"
        text += "Help for motors in the Gantry. \n"
        text += "See the specific information in the relative documentation.\n"
        text += "Some useful info:\n"
        text += " X = 5,     Coordinate System:  3, units: microns.\n"
        text += " Y = 6,     Coordinate system: 3 units: microns.\n"
        text += " Z = Z,     Coordinate system: 1, moves the RTT stage up and down, units: microns.\n"
        text += " Roll = A,  Coordinate System: 1, tips the RTT stage towards front or back, i.e. rotation around X axis, units: degrees.\n"
        text += " Pitch = B, Coordinate System: 1, tilts the RTT stage towards left and right, i.e. Rotation around Y axis, units: degrees.\n"
        text += " Rot = C,   Coordinate System: 2, rotation around Z axis, units: degrees.\n"
        text += " \n"
        text += " All motions are in linear mode, i.e. slow, by default, unless specified explicitly otherwise."

        return(text)


class LaserHelp():
    """
    A Coherent OBIS helper class, defining a dictionary which contains:
    Python command      SCPI command        Short Explanation       Possible Values         Manual page

    A further method is used to output the Description of a command.
    The possible values are explained in the file commandslits.txt. The Obis_Commands.txt contains an extraction from the manual
    of all allowed commands

    The .txt files must be stored in a directory Hardware/HWDOCS/OBIS-LX relative to the one where the .py file resides.
    The file obis_commands.py is a translation of the SCPI commands into something generic python can understand.

    M. Altissimo - 03 June 2024
    """
    def __init__(self):

        self.file_path = "Hardware/HWDocs/OBIS-LX/"
        self.filename = self.file_path + "Obis_Commands.txt"
        self.myfile = self.file_path + "commandlist.txt"

        self.commands = self.read_txt(self.filename)
        self.values = self.read_possible_values( self.myfile)
        self.help_dict = self.Laser_commands(obis_commands)

    def read_txt(self, filename):
        data = {}
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line.strip()
                parts = line.split()
                man_page_number = parts[-1]
                command = parts[0]
                description = ' '.join(parts[1:-1])
                data[command] = [description, man_page_number]
            file.close()
        return (data)

    def read_possible_values(self, myfile):
        data = {}
        with open(myfile, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line.strip()
                parts = line.split()
                command = parts[0]
                value = ' '.join(parts[1:])
                data[command] = value
            file.close()
        return (data)

    def Laser_commands(self, module):
        commands = {}
        for pyname, SCPI_name in inspect.getmembers(module):
            if not pyname.startswith('__') and isinstance(SCPI_name, str):
                description = f" Description for {pyname}"
                possible_values = self.values[SCPI_name]
                commands[pyname] = [SCPI_name, self.commands[SCPI_name][0], possible_values, self.commands[SCPI_name][1]]
        return commands

    def obis_command_help(self, command_input):
        """
        This allows the user to inpout either the pyName or the SCPI name of a command.

        :param commands_dict: a dictionary as defined by the Laser_commands method
        :param command_input: a query from the user for a description.
        :return: the description of the command_input

        """

        if command_input in self.help_dict:
            return self.help_dict[command_input[1]]

        for details in self.help_dict.values():
            if details[0] == command_input:
                answer  = details[1] + ". Details can be found on page " +  details[3] + " of the Obis Operator Manual"
                return(answer)


    #values = read_possible_values(myfile)

    #full_help = Laser_commands(obis_commands, commands, values)
    def print_Obis_help(self):
        for key, value in self.help_dict.items():
            print(f"{key}: {value[0]}\tDescription: {value[1]}\t Default Value: {value[2]}\t Man page: {value[-1]}\n")
