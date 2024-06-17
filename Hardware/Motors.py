
from Communication.MCG import Gantry as gc
import numpy as np
import time
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

Further to this, here below the motor definitions for the specific Gantry in use at Elettra

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
"""
class Initer():
   
    This class is designed to interrogate the PMAC about the number of motors and their respective CS's.
    The result of this is store in an 2D numpy array [[ CS, motornumber, motorname]]
    The array can be then traversed to get, for each valid motor of the PMAC:
    ishomed?
    home position?
    jog speed
    plus limit
    minus limit
    Once this is known, it creates an object of class Motor(see below) with the appropriate naming and properties.
    """

    """
    
    MOVED THE CODE INTO THE MotorUtil class, seemed more reasonable
    
   pass
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

    def __init__(self, connection, motorID=9, ishomed=False, motorname=None, cs=0, pmac_name= None, act_pos=0.0, jogspeed=0.0,
                 homepos=0, real_pos = 0.0):
        """ Init function for the motor object. In the QSYS convention the RTT stage has 4 motors:
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

         :param connection: a shell for communicating with the pmac.
         :param motorID: the ID (integer), allowed values from 1 to 6 for Elettra Gantry
         :param cs: Coordinate System in the Pmac Convention
         :param ishomed: flag to specify whether the motor has been homed or not. Refer to motor[x].HomeComplete.
         :param motorname: this is internal, and needed for comms with the Pmac. must be inited with form "motor_X",
                         where X is the motorID above
         :param pmac_name: name of the motor converted into the PPMAC convention, i.e. motor[i]
         :param act_pos: position value for the outer servo loop. WITH corrections (table comp and backlash).
         :param jogspeed: speed magnitude of a jog move, or a programmed "rapid" move
         :param homepos: is the motor reference position after powerup and init (in motorunits).
         :param real_pos: act_pos - homespos
         """


        self.connection = connection # a shell, possibly active...
        self.motorID = motorID  # set by default to 9, as motor number 9 is not present on the machine.
        # self.mode = mode
        # self.speed = speed
        self.cs = cs  # this is the Coordinate System for each motor
        # refer to page 983 Motor[x].HomeComplete of PMAC Software reference Manual. Set to False for safety
        if motorID is None:
            self.motorname = motorname
            self.pmac_name = pmac_name
            self.atc_pos = act_pos
            self.jogspeed = jogspeed
            self.homepos = homepos
            self.ishomed = ishomed
            self.real_pos = real_pos
        elif motorID is not None:
            self.motorname = "Motor_" + str(motorID)  # this is internal, and needed for comms with the Pmac
            self.pmac_name = self.motor_conv()
        if self.pmac_name is not None:
            self.ishomed = self.homecomplete()
            self.act_pos = self.get_pos()
            self.jogspeed = self.getjogspeed()
            self.homepos = self.get_homepos()
            self.real_pos = self.calc_real_pos()

    @classmethod
    def sr_check(cls, axis):
        """
        This checks the axis (X, Y, Z, Roll, etc) the user wants to move, and detects the System of Reference for the move
        according to the QSYS convention specified above.

        :param axis: a string specifying the axis to be moved.
        :param cls: the class itself
        :return: an int value for the system of reference of the selected axis.
        """
        axis = axis.lower()
        if axis == "x" or axis == "y":
            sr = str(3)
        elif axis == "pitch" or axis == "roll" or axis == "z":
            sr = str(1)
        elif axis  == "rot" or axis == "rotation":
            sr = str(2)

        return (sr)

    @classmethod
    def speed_check(cls, speed):
        """
        this should output as default a linear, i.e.  a slow movement

        :param cls: the class itself
        :param speed: a string, either rapid or linear
        :return: a string useful for composing a move
        """
        if speed in ["Rapid", "rapid", "fast", "Fast"]:
            out = "rapid"
        else:
            out = "linear"
        return out

    @classmethod
    def mode_check(cls, mode):
        """
        This should output inc as default, i.e. a relative move, avoiding the user sending a motor to the moon.
        :param mode: a string, either abs or inc
        :return: a string useful for composing a move
        """
        if mode in ["Absolute", "ABS", "absolute", "Abs", "abs"]:
            out = "abs"
        else:
            out = "inc"
        return out

    @classmethod
    def axis_conversion(cls, axis):
        """
        Converts axis as input by user back into Pmac-understandable format


        :param cls: the class itself
        :param axis: X, Y, Z, pitch, roll, rot
        :return: X,Y, Z, A, B, C depending on the user choice
        """
        axis = str(axis).lower()
        if axis =="x":
            ret = "X"
        elif axis == "y":
            ret = "Y"
        elif axis == "z":
            ret = "Z"
        elif axis == "pitch":
            ret = "B"
        elif axis == "roll":
            ret = "A"
        elif axis == "rot" or axis == "rotation" or axis == "yaw":
            ret = "C"
        return (ret)

    def motor_conv(self):
        index = self.motorname[-1]
        return (self.motorname[:len(self.motorname) - 2] + "[" + index + "]")

    def get_pos(self):
        """
        enquiry about the position of a motor Sends the following command to the gantry, and returns the answer:
        Motor[i].ActPos

        :return: ActPos, in motor units
        """
        message = self.pmac_name + ".ActPos"+ "\n"
        alan = float(self.connection.send_receive(message))
        self.act_pos = alan
        return(alan)

    def move_rel_one_axis (self, axis, speed, distance="0"):
        """
                See motor definition above!!!
                This method outputs a command for moving ONE AXIS only. It is possible to move more than one axis i.e.
                &1 cpx rapid abs A-1 B15 Z13400  but this will be implemented later
                This is an "inc" move, i.e. relative.

                :param axis: axis for motion
                :param speed: linear (i.e. slow, pmac default) or rapid.
                :param distance: distance of motion
                :return: a string containing the move, to be passed to a shell for execution by the PPMAC
                """
        move = f'&{str(self.cs)} cpx {str(speed)} inc {self.axis_conversion(axis)}{distance}\n'

        """move += str(self.cs)
        move += "cpx "
        move += str(speed)
        move += " inc "
        move += " "
        move += self.axis_conversion(axis)
        move += " "
        move += str(distance)
        move += "\n"
        # The next lines are for debugging
        # print(command)
        # output = str("Move: " + command + " sent as requested")"""
        return (move)

    def move_abs_one_axis (self, axis, speed, coordinate="0"):
        """
                See motor definition above!!!
                This method outputs a command for moving ONE AXIS only. It is possible to move more than one axis i.e.
                &1 cpx rapid abs A-1 B15 Z13400  but this will be implemented later
                This is an "inc" move, i.e. relative.

                :param axis: axis for motion
                :param speed: linear (i.e. slow, pmac default) or rapid.
                :param distance: distance of motion
                :return: a string containing the move, to be passed to a shell for execution by the PPMAC
                """
        move = f'&{str(self.cs)} cpx {str(speed)} abs  {self.axis_conversion(axis)}{coordinate}\n'

        return(move)

    def calc_real_pos(self):
        """
        Calculates the motor position relative to the zero, i.e. the home pos.
        Motor[x].ActPos - Motor[X].HomePos
        :return: a float value, with the motor position.
        """
        calc = self.act_pos - self.homepos
        self.real_pos = calc
        return(calc)

    def stop(self):
        """
        stops the motor from moving
        :return:
        """
        pass

    def homecomplete(self):
        """
        checks if the home search has been completed. 1 -> True, 0 -> False

        :return: the result of the check, either True or False.
        """
        command = str(self.pmac_name) + ".HomeComplete"
        result = int(self.connection.send_receive(command))
        if result == 1:
            self.ishomed = True
        else:
            self.ishomed = False
        return(result)

    def get_homepos(self):
        """
        Enquiries the PMAC as to what the home position of the motor is
        :return: the home coordinate
        """
        command = str(self.pmac_name) + ".HomePos"
        result = float(self.connection.send_receive(command))
        self.homepos = result
        return (result)

    def setjogspeed(self, value):
        """
        Sets the jogspeed of the motor to a user-specified value
        :param value: Float, user-input
        :return: Changes the status of the jogspeed property
        """
        old_speed = self.getjogspeed()
        command = str(self.pmac_name) + ".jogspeed=" + str(value)
        result = self.connection.send_receive(command)
        if result != value:
            self.jogspeed = old_speed
        else:
            self.jogspeed = value

    def getjogspeed(self):
        """
        Enquiries the system as to what is the current set jogspeed for the motor
        :return: the value of the motor.
        """
        command = str(self.pmac_name) + ".jogspeed"
        alan = float(self.connection.send_receive(command))
        self.jogspeed = alan
        return(alan)


class CompMotor():
    """

    This is Elettra-system specific, since motors 1 2 and 3 are combined into axes A, B and Z, this class reflects that
    architecture. It is a simpler class than Motor, since a lot of the parameters of the single motors are lost
    in the definition of the axes. See the Pmac Software Reference  and the Pmac Users Manuals for detailed description.

    """

    def __init__(self,connection = None, pmac_name = None, cs = 1, real_pos = 0.0, ishomed = 0):
        """
        :param connection: an active shell towards the pmac
        :param pmac_name: A, B or Z for roll, pitch and Z lift (see GantryHelp for info)
        :param cs: the coordinate system for the composite motor.Only acceptable value is 1.
        :param real_pos: the position of each motor. Must be from &1 p command,and decconstructed correctly.
        :param ishomed: from Coord[1].HomeComplete
        """
        self.connection = connection
        if connection.alive == False:
            raise ValueError("Connection to PMAC not active, inizialization impossible")
        self.pmac_name = pmac_name # must be inited by user, either A, B or Z.
        if pmac_name is not "A" or "a" or "B" or "b" or "Z" or "z":
            raise ValueError("The allowed names are only A, B or Z!")
        self.cs = cs
        if self.cs != 1:
            raise ValueError("The Coordinate system should be 1 @ Elettra!")
        self.real_pos = self.get_real_pos()
        self.ishomed = self.homecomplete()

    def get_real_pos(self):
        getpos = "&1 p"
        full = self.connection.send_receive(getpos)
        split = full.split()
        if pmac_name is not None:
            if self.pmac_name == "A":
                pos = split[0][1:]
            elif self.pmac_name == "B":
                pos = split[1][1:]
            elif self.pmac_name == "Z":
                pos = split[2][1:]
        else:
            raise ValueError("MotorName not initialized correctly!! Must be either A, B or Z")

        self.real_pos = float(pos)
        return(float(pos))

    def homecomplete (self):

        ret = self.connection.send_receive("Coord[" + self.cs + "].HomeComplete")
        self.ishomed = ret
        return(ret)

class MotorUtil():
    """
    A collection of motor utilities for the LTP.
    """

    def __init__(self, connection, stillhoming = 1, motor = None):
        self.connection = connection # an active PMAC shell.
        if connection.alive == False:
            raise ValueError("Connection to PMAC not active, inizialization impossible")
        self.stillhoming = stillhoming
        self.motor = motor

    def homeinprog(self):
        """

        :return:
        """
        out = [5]*3
        for i in range (3):
            mess = "Coord[" + str(i+1) + "].HomeInProgress"
            out[i] = self.connection.send_receive(mess)
        ret = all(el  == out[0] for el in out)
        return(ret)

    def gantryHomed(self):
        """
        Checks all the CS of the Gantry asking whether the home is completed.
        :return: True( or 1) if and only if all the CS's motors are homed.
        """
        out = [5] * 3
        for i in range(3):
            mess = "Coord[" + str(i+1) + "].HomeComplete
            out[i] = self.connection.send_receive(mess)
        ret = all(el == out[0] for el in out)
        return (ret)

    def motors(self):
        """
        This method enquiries the PMAC to get the number of motors on the system. At this stage, only 12 motors are
        allowed at maximum. The Gantry at elettra has only 6, so there is ample space for further extension.
        :return: motors, an array with motor nr and its CS its pmac name [ CS, motornumber, motorname]
        Moved from the Initer class, it didn't make sense to have another class.
        """
        rawarray = []
        motors = []
        no_motor_index = []
        for i in range (12):
            mess = '#'+str(i)+'->'
            self.connection.send_message(mess)
            self.connection.textoutput = []
            time.sleep(0.01)
            self.connection.receive_message()
            rawarray.append(self.connection.textoutput[1]) # This initializes the array with all the outputs from interrogating the Pmac

        for i in range(len(rawarray)):
            if rawarray [i][0] == "&":
                motors.append([rawarray[i][1], rawarray[i][3], rawarray[i][-1]]) # This is the list of motors present on the System.
                                                            # motors[i][0] is the CS of motor nr motors[i][1], named motors[i][2] in the PMAC convention
        return(motors)

    def check_in_pos(self):
        if self.motor is not None:
            mess = "Coord[" + self.motor.cs + "].InPos" # Using the CS, as it's more versatile than addressing the single motor
            out = self.connection.send_receive(mess)
        else:
            raise ValueError("No motors specified!")
        return (out)


class Move():

    def __init__(self, connection, motor = None, compmotor = None, cs = 0, name = None, util = None, movecomplete = True):
        self.connection = connection
        if connection.alive == False:
            raise ValueError("Connection to PMAC not active, inizialization impossible")
        self.motor = motor # object fo class Motor
        self.compmotor = compmotor # object of class CompMotor
        self.cs = 0
        self.util = util # an object of class MotorUtil
        self.movecomplete = movecomplete
        self.name = name
        if self.motor is not None:
            self.cs = self.motor.cs()
            self.name = self.motor.motorID
            if self.motor.motorID <= 3:
                raise Warning("Addressing single motors in the RTT stage, care must be taken!!")
        elif self.compmotor is not None:
            self.cs = self.compmotor.cs
            self.name = self.compmotor.pmac_name

    def move_rel(self, speed = "rapid", distance = 0.0):
        #Composing the message  to be sent:
        move = f'&{str(self.cs)} cpx {(speed)} inc {self.name} {distance}\n'
        original_pos = self.motor.real_pos
        self.connection.send_message(move)
        self.movecomplete = False
        while not self.movecomplete:
            time.sleep(0.005)
            self.movecomplete = self.util.check_in_pos()

        #Updating values in the objects:
        if self.motor is not None:
            self.motor.act_pos = self.motor.get_pos
        elif self.compmotor is not None:
            self.compmotor.real_pos = self.compmotor.get_real_pos()

    def move_abs(self, speed = "rapid", coord =0.0):
        # Composing the message  to be sent:
        move = f'&{str(self.cs)} cpx {(speed)} abs {self.name} {distance}\n'
        original_pos = self.motor.real_pos
        self.connection.send_message(move)
        self.movecomplete = False
        while not self.movecomplete:
            time.sleep(0.005)
            self.movecomplete = self.util.check_in_pos()
        if self.motor is not None:
            self.motor.act_pos = self.motor.get_pos
        elif self.compmotor is not None:
            self.compmotor.real_pos = self.compmotor.get_real_pos()






