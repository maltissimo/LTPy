import obis_commands
import inspect

"""
Here below some helper function, defining a dictionary which contains: 
Python command      SCPI command        Short Explanation       Possible Values         Manual page

A further function is used to output the Description of a command.
The possible values are explained in the file commandslits.txt. The Obis_Commands.txt contains an extraction from the manual
of all allowed commands 

The .txt files must be stored in a directory HWDOCS/OBIS-LX relative to the one where the .py file resides. 
The file obis_commands.py is a translation of the SCPI commands into something generic python can understand. 

M. Altissimo - 03 June 2024
"""
def read_txt(filename):
    data = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line.strip()
            parts = line.split()
            man_page_number = parts[-1]
            command = parts[0]
            description = ' '.join(parts[1:-1])
            data [command] = [description, man_page_number]
        file.close()
    return(data)

def read_possible_values(myfile):
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
    return(data)

def Laser_commands(module, command, values):
    commands = {}
    for pyname, SCPI_name in inspect.getmembers(module):
        if not pyname.startswith('__') and isinstance(SCPI_name, str):
            description = f" Description for {pyname}"
            possible_values = values[SCPI_name]
            commands [pyname] = [SCPI_name, command[SCPI_name][0], possible_values, command[SCPI_name][1]]
    return commands

def command_help(commands_dict, command_input):
    """
    This allows the user to inpout either the pyName or the SCPI name of a command.

    :param commands_dict: a dictionary as defined by the Laser_commands method
    :param command_input: a query from the user for a description.
    :return: the description of the command_input

    """

    if command_input in commands_dict:
        return commands_dict[command_input[1]]

    for details in commands_dict.values():
        if details[0] == command_input:
            return(details[1])


path = "HWDocs/OBIS-LX/"
filename = path + "Obis_Commands.txt"
commands = read_txt(filename)

myfile = path + "commandlist.txt"
values = read_possible_values(myfile)

full_help = Laser_commands(obis_commands, commands, values)

for key, value in full_help.items():
    print(f"{key}: {value[0]}\tDescription: {value[1]}\t Default Value: {value[2]}\t Man page: {value[-1]}\n")
