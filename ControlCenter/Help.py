
def Gantryhelp(cls):
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
    text += " Motor     PMAC Name   Coord. System   Units               Movement "
    text += "\n"
    text += "   X           5               3         µm                 Horizontal "
    text += "\n"
    text += "   Y           6               3         µm                Front-Back"
    text += "\n"
    text += "   Z           Z               1         µm                 RTT up/down"
    text += "\n"
    text += " Roll          A               1       degrees      X rot, tips RTT front/back"
    text += "\n"
    text += " Pitch         B               1       degrees      Y rot, tilts RTT left/right"
    text += "\n"
    text += " Yaw           C               2       degrees      Z rot, RTT around its axis"
    return(text)

def Motor():

    text =""
    text += "See the specific information in  see the relative documentation."
    text += "Some useful info:"
    text += " X = 5,     Coordinate System:  3, units: microns."
    text += " Y = 6,     Coordinate system: 3 units: microns."
    text += "Z = Z,     Coordinate system: 1, moves the RTT stage up and down, units: microns."
    text += " Roll = A,  Coordinate System: 1, tips the RTT stage towards front or back, i.e. rotation around X axis, units: degrees."
    text += " Pitch = B, Coordinate System: 1, tilts the RTT stage towards left and right, i.e. Rotation around Y axis, units: degrees."
    text += " Rot = C,   Coordinate System: 2, rotation around Z axis, units: degrees."
    text += " \n"
    text += " All motions are in linear mode, i.e. slow, by default, unless specified explicitly otherwise."

    return(text)