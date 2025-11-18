
import time

from ControlCenter import MathUtils
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from ControlCenter.MultiThreading import MoveWorker
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

         home_pos = gpascii.get_variable"Motor[i].HomePos)

     See the LTPy.mdj file for class basic design

     Author M. Altissimo c/o Elettra Sincrotrone Trieste SCpA
     """

    def __init__(self, connection, motorID=9, ishomed=False, motorname=None, cs=0, pmac_name=None, act_pos=0.0,
                 jogspeed=0.0,
                 homepos=0, real_pos=0.0):
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

        self.connection = connection  # a shell, possibly active...
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
            # if self.motorID == 4:
            self.motorname = "C"
        elif self.motorID == str(5):
            # elif self.motorID == 5:
            self.motorname = "X"
        elif self.motorID == str(6):
            # elif self.motorID == 6:
            self.motorname = "Y"
        self.pmac_name = "Motor[" + str(self.motorID) + "]"
        if self.pmac_name is not None:
            self.ishomed = self.homecomplete()
            self.act_pos = self.get_pos()
            self.jogspeed = self.getjogspeed()
            self.homepos = self.get_homepos()
            self.real_pos = self.get_real_pos()

    def __str__(self):
        return f"Single motor: connection = {self.connection}, motorID= {self.motorID}, coordinate system = {self.cs},\
                real position = {self.real_pos}, home completed = {self.ishomed}"

    def motor_conv(self):
        index = self.motorname[-1]
        return (self.motorname[:len(self.motorname) - 2] + "[" + index + "]")

    def get_pos(self, max_tries=20):
        """
        enquiry about the position of a motor Sends the following command to the gantry, and returns the answer:
        Motor[i].ActPos

        :return: ActPos, in motor units
        """
        message = self.pmac_name + ".ActPos" + "\n"
        # print(message)
        pos = self.connection.send_receive(message)
        attempts = 0
        while attempts < max_tries:
            try:
                alan = float(pos)
                self.act_pos = alan
                return alan
            except ValueError as e:
                attempts += 1
                err_message = (f"Error: Unable to convert '{pos}' to float. Attempt {attempts} of {max_tries}. Retrying...")
                mess_window = myWarningBox(title = "Conversion error!",
                                           message = err_message)
                mess_window.show_warning()
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
        return (calc)

    def stop(self):
        self.connection.send_receive("#"+ str(self.pmac_name) + "abort")

    def homecomplete(self):
        """
        checks if the home search has been completed. 1 -> True, 0 -> False

        :return: the result of the check, either True or False.
        """
        #print(self.pmac_name)
        command = str(self.pmac_name) + ".HomeComplete"
        #print("Home complete request command issued:, ", command, "\n")
        result = int(self.connection.send_receive(command))
        #print("Home complete request result: ", result)
        if result == 1:
            self.ishomed = True
        else:
            self.ishomed = False
        return (result)

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
        old_speed = self.jogspeed
        setcommand = str(self.pmac_name) + ".jogspeed=" + str(value)
        self.connection.send_receive(setcommand)
        result = self.getjogspeed()
        if result != value:
            self.jogspeed = old_speed
        else:
            self.jogspeed = value

    def getjogspeed(self):
        """
        Enquiries the system as to what is the current set jogspeed for the motor
        :return: the value of the motor.
        """
        maxtries = 20
        command = str(self.pmac_name) + ".jogspeed"
        for attempt in range(maxtries):
            alan = (self.connection.send_receive(command))
            if MathUtils.is_float(alan):
                self.jogspeed = float(alan)
                return (float(alan))
            else:
                pass


class CompMotor():
    """

    This is Elettra-system specific, since motors 1 2 and 3 are combined into axes A, B and Z, this class reflects that
    architecture. It is a simpler class than Motor, since a lot of the parameters of the single motors are lost
    in the definition of the axes. See the Pmac Software Reference  and the Pmac Users Manuals for detailed description.

    """

    def __init__(self, connection=None, pmac_name=None, cs=1, real_pos=0.0, ishomed=0):
        """
        :param connection: an active shell towards the pmac
        :param pmac_name: A, B or Z for roll, pitch and Z lift (see GantryHelp for info)
        :param cs: the coordinate system for the composite motor.Only acceptable value is 1.
        :param real_pos: the position of each motor. Must be from &1 p command,and decconstructed correctly.
        :param ishomed: from Coord[1].HomeComplete
        """
        self.connection = connection
        if self.connection.alive == False:
            conn_emessage = "Connection to PMAC not active, inizialization impossible"
            conn_ewindow = myWarningBox(title = "Connection error!",
                                        message = conn_emessage)
            conn_ewindow.show_warning()

        self.pmac_name = pmac_name  # must be inited by user, either A, B or Z.
        if pmac_name.lower() not in ["a", "b", "z"]:
            cap_emessage ="The allowed names are only A, B or Z!"
            cap_ewindow = myWarningBox(title = "Error!",
                                       message = cap_emessage)
            cap_ewindow.show_warning()
        self.cs = cs
        if self.cs != 1:
            cs_emessage = "The Coordinate system should be 1 @ Elettra!"
            cs_ewindow = myWarningBox(title = "Error!",
                                      message = cs_emessage)
            cs_ewindow.show_warning()
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
            pos_emessage = "MotorName not initialized correctly!! Must be either A, B or Z"
            pos_ewindow = myWarningBox(title = "Init issue!",
                                       messge = pos_emessage)
            pos_ewindow.show_warning()

        self.real_pos = float(pos)
        return (float(pos))

    def homecomplete(self):

        ret = self.connection.send_receive("Coord[" + str(self.cs) + "].HomeComplete")
        self.ishomed = ret
        return (ret)


class MotorUtil():
    """
    A collection of motor utilities for the LTP.
    """

    def __init__(self, connection, stillhoming=1, motor=None):
        self.connection = connection  # an active PMAC shell.
        if self.connection.alive == False:
            conn_wmessage = "Connection to PMAC not active, inizialization impossible!"
            conn_wwindonw = myWarningBox(title = "Connection error!",
                                         message = conn_wmessage)
            conn_wwindonw.show_warning()
        self.stillhoming = stillhoming
        self.motor = motor

    def __str__(self):
        return f"MotorUtilities: connection = {self.connection}"

    def homeinprog(self):
        """

        :return:
        """
        out = [5] * 3
        for i in range(3):
            mess = "Coord[" + str(i + 1) + "].HomeInProgress"
            out[i] = self.connection.send_receive(mess)
        ret = all(el == out[0] for el in out)
        return (ret)

    def gantryHomed(self):
        """
        Checks all the CS of the Gantry asking whether the home is completed.
        :return: True( or 1) if and only if all the CS's motors are homed.
        """
        out = [5] * 3
        for i in range(3):
            mess = "Coord[" + str(i + 1) + "].HomeComplete"
            out[i] = self.connection.send_receive(mess)
        ret = all(el == out[0] for el in out)
        return (ret)

    def homeGantry(self):
        self.resetGantry()
        gohome = "requestHost=requestHome"
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
        for i in range(12):
            mess = '#' + str(i) + '->'
            self.connection.send_receive(mess)
            #print(mess)
            """self.connection.textoutput = []
            #time.sleep(0.01)
            self.connection.receive_message()"""
            #print(self.connection.textoutput)
            rawarray.append(self.connection.textoutput[1])  # This initializes the array with all the outputs from interrogating the Pmac
            #print(self.connection.textoutput[1])
        for i in range(len(rawarray)):
            if rawarray[i][0] == "&":
                motors.append([rawarray[i][1], rawarray[i][3],
                               rawarray[i][-1]])  # This is the list of motors present on the System.
                # motors[i][0] is the CS of motor nr motors[i][1], named motors[i][2] in the PMAC convention
        return (motors)


class Move():

    def __init__(self, connection, motor=None, cs=0, name=None, util=None, movecomplete=True):
        self.connection = connection
        if connection.alive == False:
            conn_emessage = "Connection to PMAC not active, inizialization impossible"
            conn_ewindow = myWarningBox(title = "Connection error",
                                        message = conn_emessage)
            conn_ewindow.show_warning()

        self.motor = motor  # object fo class Motor or CompMotor
        self.cs = 0
        self.util = util  # an object of class MotorUtil
        self.movecomplete = movecomplete
        self.name = name
        if hasattr(self.motor, "motorID"):
            self.cs = self.motor.cs
            self.name = self.motor.motorname
            if int(self.motor.motorID) <= 3:
                mot_wmessage = "Addressing single motors in the RTT stage, care must be taken!!"
                mot_wwindow = myWarningBox(title = "Motor warning!",
                                           message = mot_wmessage)
        else:
            self.cs = self.motor.cs
            self.name = self.motor.pmac_name

    def _init_worker(self, move_cmd):
        def send_move_command():
            self.connection.send_message(move_cmd)

        self.worker = MoveWorker(self)

        self.worker.begin_signal.connect(send_move_command)
        self.worker.update_signal.connect(self._on_update_inpos)
        self.worker.end_signal.connect(self._on_move_complete)
        self.worker.error_signal.connect(self._on_move_error)

    def move_rel(self, speed="rapid", distance=0.0):
        self.movecomplete = False
        if isinstance(self.motor, Motor):
            move = f'&{str(self.cs)} cpx {speed} inc {self.name} {distance}\n'
            #print("called move: ", move)
            self._init_worker(move)
            self.worker.start()
            """#movetime = abs(distance) / self.motor.getjogspeed()  # jogspeed is in microns/ms for X, Y and Z, deg/ms for pitch, roll and yaw
            # Composing the message  to be sent:
            move = f'&{str(self.cs)} cpx {(speed)} inc {self.name} {distance}\n'
            # print("move command issued: ", move)
            self.connection.send_receive(move)
            # time.sleep(movetime * 1.1 / 1000)  # movetime is in ms, time.sleep requires s. Adding a 10% for safety/
            while not self.check_in_pos():
                self.movecomplete = False
            #print("Move ", move, " complete")
            self.movecomplete = True"""

        else:

            # Composing the message  to be sent:
            move = f'&{str(self.cs)} cpx {speed} inc {self.name} {distance}\n'
            self._init_worker(move)
            self.worker.start()
            """#time.sleep(0.5)  # half a second wait time for rotational moves, seems ok.
            # print("move command issued: ", move)
            while not self.check_in_pos():
                self.movecomplete = False
            self.movecomplete = True"""

    def move_abs(self, speed="rapid", coord=0.0):
        self.movecomplete = False

        # Composing the message  to be sent:
        move = f'&{str(self.cs)} cpx {speed} abs {self.name} {coord}\n'
        self._init_worker(move)
        self.worker.start()
        """ while not self.check_in_pos():
            self.movecomplete = False
        self.movecomplete = True"""

    def _on_update_inpos(self, in_pos):
       pass
        # Optional: update GUI or log status

    def _on_move_complete(self):
        #print("[complete] Move completed.")
        self.movecomplete = True
        # Optional: trigger GUI updates or callbacks

    def _on_move_error(self, error_msg):
        move_error = myWarningBox(title = "Move error!", message = f"[error] MoveWorker reported: {error_msg}")
        move_error.show_warning()
        # Optional: show a warning dialog


    def check_in_pos(self, max_retries=15):
        if self.motor is not None:
            mess = "Coord[" + str(self.motor.cs) + "].InPos"

            for attempt in range(max_retries):
                out = self.connection.send_receive(mess)
                #print(f"Attempt {attempt + 1}, received output: {out}")
                #print("check_in_pos output: ", out)

                try:
                    value = int(out.strip())
                    if value in (0,1):
                        #print("Check in pos final value: ", value)
                        return value
                except ValueError:
                    pass
                    #print(f"Still moving...")

                #print("Retrying...")

            #print("Max retries reached with invalid responses.")
            return 1  # default/fallback return

        else:
            mot_emessaage = "No motors specified!"
            mot_ewindow = myWarningBox(title="Motor issues!", message=mot_emessaage)
            mot_ewindow.show_warning()
            return 0





