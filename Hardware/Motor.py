from Communication.MCG import Gantry_Connection as gc
"""
These are some global definitions that may be useful during measurements. The values are taken 
directly from the config file of the Gantry PMac. It can be found inside the 
390-main/code/10420-01/LTP-RTT/LTP-RTT/Configuration 
folder

The units of measurements (PosUnits) are as follows (taken from the PowerBrik LV Arm User Manual, page 150>

Motor[x].PosUnit            Unit Name
0                        m.u.       (motor unit)
1                            Count      (ct)
2                            Meter      (m)
3                         Millimiter    (mm)
4                         Micrometer    (µm)
5                         Nanometer     (nm)
6                         Picometer     (pm)
7                              Inch     (in)                           
8                           mil         (in/1000)
9                           Revolution
10                          Radian      (rad)
11                          Degree      (deg)
12                          Gradian     (grad)
13                          Arcminute   (')
14                          Arcsecond   ('')

Further to this, here below the motor definitions: 

// [MOTOR_DEF]
&0#0->0
&1#1->i
#2->i
#3->i
&2#4->c
&3#5->x
#6->y
&0#7->0
#8->0
#9->0
#10->0
#11->0
#12->0

Author M. Altissimo c/o Elettra Sincrotrone Trieste SCpA

"""
class Motor():
    """
    This class describes a generic motor on the Gantry, as specified in the PPMAC hardware (see the relative documentation).
    Some useful info:
     X = 5,     Coordinate System:  3, units: microns
     Y = 6,     Coordinate system: 3 units: microns
     Z = Z,     Coordinate system: 1, moves the RTT stage up and down, units: microns
     Roll = A,  Coordinate System: 1, tips the RTT stage towards front or back, i.e. rotation around X axis, units: degrees
     Pitch = B, Coordinate System: 1, tilts the RTT stage towards left and right, i.e. Rotation around Y axis, units: degrees
     Rot = C,   Coordinate System: 2, rotation around Z axis, units: degrees

    All motions are in linear mode, i.e. slow, by default, unless specified explicitly otherwise.

    Each motor should be instantiated once and once only for each LTPy instance.
    The position of motor i can be accessed at any time as:

        act_position = 'Motor[i].ActPos

    Actual position must be derived from this and the homing position:

        hom(e_pos = gpascii.get_variable"Motor[i].HomePos)

    See the LTPy.mdj file for class basic design

Author M. Altissimo c/o Elettra Sincrotrone Trieste SCpA
    """

    def __init__(self, motorID=9, speed = "linear", mode = "inc", ishomed = False, motorname, pmac_name, act_pos, jogspeed, minuslimit,
                 pluslimit, homepos):
        """
        Init function for the motor object. In the QSYS convention the RTT stage has 4 motors:
        1, 2 and 3 are combined together in motors A, B and Z providing Roll/Tip, Pitch/Tilt rotations and translation along
        Z axis respectively.
        C is the rotation motor of the RTT stage, which rotates the stage around the Z (i.e. the vertical) axis.

         X = 5,
         Y = 6,
         Z = Z,
         Roll = A,
         Pitch = B,
         Rot = C,

        By default the object is initialized to a non-existing motor (nr 9)
        the others are set to defaults as it looks best this way from a safety perspective.

        :param motorID: the ID (integer), allowed values from 1 to 6
        :param speed: can be "linear" i.e. slow or "rapid"
        :param mode: relative "inc" or absolute "abs"
        :param ishomed: flag to specify whether the motor has been homed or not. Refer to motor[x].HomeComplete.
        :param motorname: this is internal, and needed for comms with the Pmac. must be inited by user with form "motor_X",
                        where X is the motorID avbove
        :param pmac_name: name of the motor converte into the PPMAC convention, i.e. motor[i]
        :param act_pos: present servo cycle's net position value for the outer servo loop. In motor units. To calculate
                        the position relative to the motor zero pos (i.e. relative to HomePos), subtract the value of .HomePos
        :param jogspeed: speed magnitude of a jog move, or a programmed "rapid" move
        :param minuslimit: minus limit of the motor encoder (in motorunits)
        :param pluslimit: plus limit of the motor encoder (in motorunits)
        :param homepos: is the motor reference position after powerup and init (in motorunits).
        """

        self.motorid = motorID # set by default to 9, as motor number 9 is not present on the machine.
        self.mode = mode
        self.speed = speed
        self.ishomed = ishomed # refer to page 983 Motor[x].HomeComplete of PMAC Software reference Manual. Set to False for safety
        self.motorname = "Motor_" + str(motorID)  # this is internal, and needed for comms with the Pmac. must be inited by user
        self.pmac_name = self.motor_conv(self.motorname)
        self.jogspeed = jogspeed
        self.minuslimit = minusliimit
        self.pluslimit = pluslimit
        self.homepos = homepos

        #TODO:  - methods to de-construct the PPMAC response to get something meaningful. here 2 typical responses:
        #       motor[2].ishomed
        #       stdin: 17:1: error  # 21: ILLEGAL PARAMETER: motor[2].ishomed
        #       motor[2].actpos
        #       Motor[2].ActPos = 1.93359375
        #       - must introduce a safety check with the air supply to the system.


        """     
            Implemented in MGC.py on 20240508
            
            - disable echoing as the output is now:
            motor[2].actpos
            Motor[2].ActPos = 1.93359375

            page 1154 of manual
            
            - methods to compile and send a message to the PPMAC.
            """





    @classmethod
    def help(cls):
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
        print(text)

    @classmethod
    def sr_check(cls, axis):
        """
        This checks the axis (X, Y, Z, Roll, etc) the user wants to move, and detects the System of Reference for the move
        according to the QSYS convention specified above.

        :param axis: a string specifying the axis to be moved.
        :return: an int value for the system of reference of the selected axis.
        """
        if axis == "X" or axis == "Y":
            sr = str(3)
        elif axis == "Pitch" or axis == "pitch" or axis == "Roll" or axis == "roll" or axis == "Z":
            sr = str(1)
        elif axis == "Rot" or axis == "rot" or axis == "rotation" or axis == "Rotation":
            sr = str(2)

        return (sr)
    @classmethod
    def axis_conversion(cls, axis):
        """
        Converts axis as input by user back into Pmac-understandable format

        :param axis: X, Y, Z, pitch, roll, rot
        :return: X,Y, Z, A, B, C depending on the user choice
        """
        if axis == "X" or axis == "x":
            ret = "X"
        elif axis == "Y" or axis == "y":
            ret = "Y"
        elif axis == "Z" or axis == "z":
            ret = "Z"
        elif axis == "PITCH" or axis == "Pitch" or axis == "pitch":
            ret = "B"
        elif axis == "ROLL" or axis == "Roll" or axis == "roll":
            ret = "A"
        elif axis == "ROT" or axis == "Rot" or axis == "rot" or axis == "Rotation" or axis == "rotation" or axis == "YAW" or axis == "Yaw" or axis == "yaw":
            ret = "C"

        return (ret)

    @classmethod
    def speed_check(cls, speed):
        """
        this should output as default a linear, i.e.  a slow movement
        :param speed: a string, either rapid or linear
        :return: a string useful for composing a move
        """
        if speed == "Rapid" or speed == "rapid" or speed == "fast" or speed == "Fast":
            out = "rapid"
        else:
            out = "linear"
        return (out)

    @classmethod
    def mode_check(cls, mode):
        """
        This should output inc as default, i.e. a relative move, avoiding the user sending a motor to the moon.
        :param mode: a string, either abs or inc
        :return: a string useful for composing a move
        """
        if mode == "Absolute" or mode == "ABS" or mode == "absolute" or mode == "Abs" or mode == "abs":
            out = "abs"
        else:
            out = "inc"
        return (out)


    def motor_conv(self, motorName):
        """
        This function converts the name of a motor to a Pmac compatible, i.e.
        Motor_i -> Motor[i]
        This is not

        :param motorName: the name of the motor to be converted into
        :return: the Pmac-Compatible name of the motor
        """
        index = motorName[-1]
        self.pmac_name = motorName[:len(motorName) - 2] + "[" + index + "]"
        return (self.pmac_name)

    def get_pos(self):
        """
        enquiry about the position of a motor Sends the following command to the gantry, and returns the answer:
        Motor[i].ActPos

        :return: ActPos, in motor units
        """
        message = motor_conv(self.motorname) + ".ActPos"+ "\n"
        ActPos = float(Communication.MCG.send_receive(message))

        return(ActPos)

    def move_1_ax(self, axis, speed, mode, length  ="0"):
        """
        See motor definition above!!!
        This method outputs a command for moving ONE AXIS only. It is possible to move more than one axis i.e.
        &1 cpx rapid abs A-1 B15 Z13400 this will be implemented later

        :param axis: axis for motion
        :param speed: linear (i.e. slow, pmac default) or rapid.
        :param mode: absolute (abs) or relative (inc)
        :param length: length of motion
        :return: a string containing the move, to be passed to a shell for execution by the PPMAC
        """
        SR = self.sr_check(axis)
        speed = self.speed_check(speed)
        mode = self.mode_check(mode)

        move = str("&" + str(SR) + " cpx " + speed + " " + mode + " " + axis_conversion(axis) + str(length) + "\n")
        #The next lines are for debugging
        #print(command)
        #output = str("Move: " + command + " sent as requested")

        return (move)


    def stop(self):
        pass

    def home(self):
        pass

    def setspeed(self):
        pass

    def getspeed(self):
        pass


