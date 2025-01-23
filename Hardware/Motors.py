
from Communication.MCG import Gantry as gc
import numpy as np
import time
import warnings

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
        if self.motorID is None:
            self.motorname = None
            self.pmac_name = pmac_name
            self.atc_pos = act_pos
            self.jogspeed = jogspeed
            self.homepos = homepos
            self.ishomed = ishomed
            self.real_pos = real_pos
        elif self.motorID == str(4):
            #if self.motorID == 4:
            self.motorname = "C"
        elif self.motorID == str(5):
            #elif self.motorID == 5:
            self.motorname = "X"
        elif self.motorID == str(6):
            #elif self.motorID == 6:
            self.motorname = "Y"
        self.pmac_name = "Motor[" + str(self.motorID) +"]"
        if self.pmac_name is not None:
            self.ishomed = self.homecomplete()
            self.act_pos = self.get_pos()
            self.jogspeed = self.getjogspeed()
            self.homepos = self.get_homepos()
            self.real_pos = self.get_real_pos()

    def __str__(self):
        return f"Composite motor: connection = {self.connection}, motorID= {self.motorID}, coordinate system = {self.cs},\
                real position = {self.real_pos}, home completed = {self.ishomed}"

    def motor_conv(self):
        index = self.motorname[-1]
        return (self.motorname[:len(self.motorname) - 2] + "[" + index + "]")

    def get_pos(self, max_tries=5):
        """
        enquiry about the position of a motor Sends the following command to the gantry, and returns the answer:
        Motor[i].ActPos

        :return: ActPos, in motor units
        """
        message = self.pmac_name + ".ActPos"+ "\n"
        #print(message)
        pos = self.connection.send_receive(message)
        attempts = 0
        while attempts < max_tries:
            try:
                alan = float(pos)
                self.act_pos = alan
                return alan
            except ValueError:
                attempts += 1
                print(f"Error: Unable to convert '{pos}' to float. Attempt {attempts} of {max_tries}. Retrying...")
                if attempts < max_tries:
                    pos = self.connection.send_receive(message)  # Retry fetching the position
                else:
                    raise ValueError(f"Failed to convert position '{pos}' to float after {max_tries} attempts.")

        # If this point is reached, it means max tries were exceeded, so raise an error.
        raise ValueError(f"Failed to retrieve a valid float position after {max_tries} attempts.")

    def get_real_pos(self):
        """
        Calculates the motor position relative to the zero, i.e. the home pos.
        Motor[x].ActPos - Motor[X].HomePos
        :return: a float value, with the motor position.
        """
        calc = self.get_pos() - self.homepos
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
        if self.connection.alive == False:
            raise ValueError("Connection to PMAC not active, inizialization impossible")
        self.pmac_name = pmac_name # must be inited by user, either A, B or Z.
        if pmac_name.lower() not in ["a", "b", "z"]:
            raise ValueError("The allowed names are only A, B or Z!")
        self.cs = cs
        if self.cs != 1:
            raise ValueError("The Coordinate system should be 1 @ Elettra!")
        self.real_pos = self.get_real_pos()
        self.ishomed = self.homecomplete()

    def __str__(self):
        return f"Composite motor: connection = {self.connection}, pmac name = {self.pmac_name}, coordinate system = {self.cs},\
               real position = {self.real_pos}, home completed = {self.ishomed}"

    def get_real_pos(self):
        getpos = "&1 p"
        full = self.connection.send_receive(getpos)
        split = full.split()
        try:
            if self.pmac_name == "A":
                pos = split[0][1:]
            elif self.pmac_name == "B":
                pos = split[1][1:]
            elif self.pmac_name == "Z":
                pos = split[2][1:]
        except ValueError:
            print("MotorName not initialized correctly!! Must be either A, B or Z")

        self.real_pos = float(pos)
        return(float(pos))

    def homecomplete (self):

        ret = self.connection.send_receive("Coord[" + str(self.cs) + "].HomeComplete")
        self.ishomed = ret
        return(ret)

class MotorUtil():
    """
    A collection of motor utilities for the LTP.
    """

    def __init__(self, connection, stillhoming = 1, motor = None):
        self.connection = connection # an active PMAC shell.
        if self.connection.alive == False:
            warnings.warn("Connection to PMAC not active, inizialization impossible")
        self.stillhoming = stillhoming
        self.motor = motor

    def __str__(self):
        return f"MotorUtilities: connection = {self.connection}"

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
            mess = "Coord[" + str(i+1) + "].HomeComplete"
            out[i] = self.connection.send_receive(mess)
        ret = all(el == out[0] for el in out)
        return (ret)

    def homeGantry(self):
        selectAxes = "selectAxes=selectAll"
        gohome = "requestHost=requestHome"
        self.connection.send_receive(selectAxes)
        time.sleep(0.07)
        self.connection.send_receive(gohome)

        """while not self.gantryHomed():
            print("still homing...")
            time.sleep(1)
        print("system homed!")"""

    def resetGantry(self):
        selectAxes = "selectAxes=selectAll"
        reset = "requestHost=requestReset"
        self.connection.send_receive(selectAxes)
        time.sleep(0.07)
        self.connection.send_receive(reset)

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


class Move():

    def __init__(self, connection, motor = None, cs = 0, name = None, util = None, movecomplete = True):
        self.connection = connection
        if connection.alive == False:
            raise ValueError("Connection to PMAC not active, inizialization impossible")
        self.motor = motor # object fo class Motor or CompMotor
        self.cs = 0
        self.util = util # an object of class MotorUtil
        self.movecomplete = movecomplete
        self.name = name
        if hasattr(self.motor, "motorID"):
            self.cs = self.motor.cs
            self.name = self.motor.motorname
            if int(self.motor.motorID) <= 3:
                raise Warning("Addressing single motors in the RTT stage, care must be taken!!")
        else:
            self.cs = self.motor.cs
            self.name = self.motor.pmac_name

    def move_rel(self, speed = "rapid", distance = 0.0):
        self.movecomplete = False
        if isinstance(self.motor, Motor):
            movetime = abs(distance) / self.motor.getjogspeed() # jogspeed is in microns/ms for X, Y and Z, deg/ms for pitch, roll and yaw
            # Composing the message  to be sent:
            move = f'&{str(self.cs)} cpx {(speed)} inc {self.name} {distance}\n'
            #print("move command issued: ", move)
            self.connection.send_receive(move)
            #time.sleep(movetime * 1.1 / 1000)  # movetime is in ms, time.sleep requires s. Adding a 10% for safety/
            while not self.movecomplete:
                time.sleep(0.005)
                self.movecomplete = self.check_in_pos()

        else:
            # Composing the message  to be sent:
            move = f'&{str(self.cs)} cpx {(speed)} inc {self.name} {distance}\n'
            self.connection.send_receive(move)
            time.sleep(0.5)  #half a second wait time for rotational moves, seems ok.
            #print("move command issued: ", move)
            while not self.movecomplete:
                time.sleep(0.005)
                self.movecomplete = self.check_in_pos()
            #self.movecomplete = self.check_in_pos()


        #Updating values in the objects:
        if hasattr(self.motor, "motorID"):
            self.motor.act_pos = self.motor.get_pos()
            #print(self.motor.act_pos)
            self.motor.real_pos = self.motor.get_real_pos()
        else:
            self.motor.real_pos = self.motor.get_real_pos()


    def move_abs(self, speed = "rapid", coord =0.0):
        # Composing the message  to be sent:
        move = f'&{str(self.cs)} cpx {(speed)} abs {self.name} {coord}\n'
        #print(move)
        #original_pos = self.motor.real_pos
        self.connection.send_message(move)
        self.movecomplete = False
        while not self.movecomplete:
            time.sleep(0.005)
            self.movecomplete = self.check_in_pos()
        if hasattr(self.motor, "motorID"):
            self.motor.act_pos = self.motor.get_pos()
            self.motor.real_pos = self.motor.get_real_pos()
        else:
            self.motor.real_pos = self.motor.get_real_pos()

    def check_in_pos(self):
        if self.motor is not None:
            mess = "Coord[" + str(self.motor.cs) + "].InPos" # Using the CS, as it's more versatile than addressing the single motor. Also, same property for Motor and Compmotor.
            out = self.connection.send_receive(mess)
        else:
            raise ValueError("No motors specified!")
        return (out)




