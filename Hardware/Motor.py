from Communication.MCG import Gantry_Connection as gc
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
    Once this is known, it create object of class Motor(see below) with the appropriate naming and properties.
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
        for i in range (0:15):
            mess = '#'+str(i)+'->'
            self.connection.send_message(mess)
            connection.textoutput = []
            time.sleep(0.01)
            self.connection.receive_message()
            rawarray.append(self.connection.textoutput[1]) # This initializes the array with all the outputs from interrogating the Pmac

        for i in len(range(rawarray)):
            motor.append(rawarra[i][1])
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

    def __init__(self, motorID=9, ishomed = False, cs = 0, pmac_name = None, act_pos= 0.0, jogspeed = 0.0, homepos = 0):
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

        :param motorID: the ID (integer), allowed values from 1 to 6 for Elettra Gantry
        :param cs: Coordinate System in the Pmac Convention
        :param ishomed: flag to specify whether the motor has been homed or not. Refer to motor[x].HomeComplete.
        :param motorname: this is internal, and needed for comms with the Pmac. must be inited by user with form "motor_X",
                        where X is the motorID avbove
        :param pmac_name: name of the motor converted into the PPMAC convention, i.e. motor[i]
        :param jogspeed: speed magnitude of a jog move, or a programmed "rapid" move
        :param homepos: is the motor reference position after powerup and init (in motorunits).
        """

        self.motorId = motorID # set by default to 9, as motor number 9 is not present on the machine.
        # self.mode = mode
        # self.speed = speed
        self.ishomed = ishomed # refer to page 983 Motor[x].HomeComplete of PMAC Software reference Manual. Set to False for safety
        #self.motorname = "Motor_" + str(self.motorID)  # this is internal, and needed for comms with the Pmac. must be inited by user
        self.cs = cs # this is the Coordinate System for each motor
        self.pmac_name = "Motor[" + str(self.motorId) + "]" # This would be Motor[xxx]
        self.jogspeed = jogspeed
        self.homepos = homepos

        # TODO: - move self.mode and self.speed somewhere else, they are not properties of a motor
        #  - must introduce a safety check with the air supply to the system.
        """
         - methods to de-construct the PPMAC response to get something meaningful. here 2 typical responses:
        #       motor[2].ishomed
        #       stdin: 17:1: error  # 21: ILLEGAL PARAMETER: motor[2].ishomed
        #       motor[2].actpos
        #       Motor[2].ActPos = 1.93359375
            Implemented in MGC.py on 20240508
            
            - disable echoing as the output is now:
            motor[2].actpos
            Motor[2].ActPos = 1.93359375

            page 1154 of manual
            
            - methods to compile and send a message to the PPMAC.
            """

    """@classmethod
    def help(cls):
    moved to ControCenter Help
       """

    @classmethod
    def sr_check(cls, axis):
        """
        This checks the axis (X, Y, Z, Roll, etc) the user wants to move, and detects the System of Reference for the move
        according to the QSYS convention specified above.

        :param axis: a string specifying the axis to be moved.
        """
        if axis == "X" or axis == "Y":
            self.cs = str(3)
        elif axis == "Pitch" or axis == "pitch" or axis == "Roll" or axis == "roll" or axis == "Z":
            self.cs = str(1)
        elif axis == "Rot" or axis == "rot" or axis == "rotation" or axis == "Rotation":
            self.cs = str(2)

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


    def motor_conv(self, motorname):
        """
        This function converts the name of a motor to a Pmac compatible, i.e.
        Motor_i -> Motor[i]
        This is not

        :param motorName: the name of the motor to be converted into
        :return: the Pmac-Compatible name of the motor
        """
        index = self.motorName[-1]
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

    def move_1_ax(self, speed, mode, length  ="0"):
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
        move = str("&" + str(self.cs) + " cpx " + str(speed) + " " + str(mode) + " " + axis_conversion(axis) + str(length) + "\n")
        #The next lines are for debugging
        #print(command)
        #output = str("Move: " + command + " sent as requested")

        return (move)

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

    def getspeed(self):
        command = str(self.pmac_name) +  ".jogspeed"
        self.jogspeed = float(gc.send_receive(command))


