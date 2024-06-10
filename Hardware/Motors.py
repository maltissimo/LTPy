from Communication.MCG import Gantry as gc
import numpy as np
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

class Initer():
    """
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
    def __init__(self, connection = None):
        if connection is None:
            self.connection = gc() # Object of class Communication.MCG.Gantry

    def  motors(self):
        """
        This method enquiries the PMAC to get the number of motors on the system. At this stage, only 15 motors are
        allowed at maximum. The Gantry at elettra has only 6, so there is ample space for further extension.
        :return: motors, an array with motor nr and its CS its pmac name [ CS, motornumber, motorname]
        """
        rawarray = []
        motor = []
        no_motor_index = []
        for i in range (15):
            mess = '#'+str(i)+'->'
            self.connection.send_message(mess)
            connection.textoutput = []
            time.sleep(0.01)
            self.connection.receive_message()
            rawarray.append(self.connection.textoutput[1]) # This initializes the array with all the outputs from interrogating the Pmac

        for i in len(range(rawarray)):
            motor.append(rawarray[i][1])
            motor.append(rawarray[i][3])
            motor.append(rawarray[i][-1])
        motor1 = np.asarray(motor)
        motors = motor1.reshape((int(len(motor)/3)),3)

        for i in range (len(motors)):
            if motors[i][-1] != str(0):
                no_motor_index.append(i)

        motors = np.delete(motors, no_motor_index, axis = 0) # This is the list of motors present on the System.
                                                            # motors[i][0] is the CS of motor nr motors[i][1], named motors[i][2] in the PMAC convention
        return(motors)


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

    def __init__(self, motorID=9, ishomed=False, motorname=None, cs=0, pmac_name= None, act_pos=0.0, jogspeed=0.0,
                 homepos=0):
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

         :param motorID: the ID (integer), allowed values from 1 to 6 for Elettra Gantry
         :param cs: Coordinate System in the Pmac Convention
         :param ishomed: flag to specify whether the motor has been homed or not. Refer to motor[x].HomeComplete.
         :param motorname: this is internal, and needed for comms with the Pmac. must be inited by user with form "motor_X",
                         where X is the motorID avbove
         :param pmac_name: name of the motor converted into the PPMAC convention, i.e. motor[i]
         :param jogspeed: speed magnitude of a jog move, or a programmed "rapid" move
         :param homepos: is the motor reference position after powerup and init (in motorunits).
         """


        self.motorID = motorID  # set by default to 9, as motor number 9 is not present on the machine.
        # self.mode = mode
        # self.speed = speed
        self.ishomed = ishomed  # refer to page 983 Motor[x].HomeComplete of PMAC Software reference Manual. Set to False for safety
        if motorname is not None:
            self.motorname = motorname
        else:
            self.motorname = "Motor_" + str(motorID)  # this is internal, and needed for comms with the Pmac. must be inited by user
        self.cs = cs  # this is the Coordinate System for each motor
        if cs != 0:
            self.cs = (self.sr_check())
        self.pmac_name = pmac_name
        if pmac_name is not None:
            self.pmac_name = pmac_name
        else:
            self.pmac_name = self.motor_conv()
        self.atc_pos = act_pos
        self.jogspeed = jogspeed
        self.homepos = homepos

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
        self.pmac_name = self.motorname[:len(self.motorname) - 2] + "[" + index + "]"

    def get_pos(self):
        """
        enquiry about the position of a motor Sends the following command to the gantry, and returns the answer:
        Motor[i].ActPos

        :return: ActPos, in motor units
        """
        message = self.motor_conv(self.motorname) + ".ActPos"+ "\n"
        self.act_pos = float(Communication.MCG.send_receive(message))

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

    def stop(self):
        pass

    def ishomed(self):
        command = str(self.pmac_name) + ".HomeComplete"
        result = int(gc.send_receive(command))
        if result == 1:
            self.ishomed = True
        else:
            self.ishomed = False

    def getpos(self):
        command = str(self.pmac_name) + ".ActPos"
        result = float(gc.send_receive(command))
        return(result)

    def homepos(self):
        command = str(self.pmac_name) + ".HomePos"
        result = float(gc.send_receive(command))
        self.homepos = result

    def setjogspeed(self, value):
        old_speed = self.getspeed()
        command = str(self.pmac_name) + ".jogspeed=" + str(value)
        result = gc.send_receive(command)
        if result != command:
            self.jogspeed = old_speed
        else:
            self.jogspeed = value

    def getjogspeed(self):
        command = str(self.pmac_name) +  ".jogspeed"
        self.jogspeed = float(gc.send_receive(command))


class Move:
    @staticmethod
    def one_axis(distance, motor = Motor()):
        """
            See motor definition above!!!
            this method moves a single axis, by relative (inc), with rapid speed.

            :param motor: axis for movement, object of class Motor
            :param distance: length of motion
            :return: a string containing the move, to be passed to a shell for execution by the PPMAC
            """

        move = ""
        move += str(self.cs)
        move += "cpx "
        move += str(speed)
        move += str(mode)
        move += " "
        move += self.axis_conversion(axis)
        move += " "
        move += str(distance)
        move += "\n"
        # The next lines are for debugging
        # print(command)
        # output = str("Move: " + command + " sent as requested")
        return (move)