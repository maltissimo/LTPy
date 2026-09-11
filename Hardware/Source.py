from Hardware.obis_commands import *
from Communication.MCL import *


class Laser (SerialConn):
    def         __init__(self, comms_on = "OFF", is_on = 'OFF', wlength = 0.0,
                         pow_level = None,
                         cur_level = None,
                         p_low_lim = None,
                         p_high_lim = None,
                         op_mode = None):
        super().__init__()
        self.comms_on = comms_on
        self.is_on = self.serialmessage(isLASON)
        self.wlength = wlength
        self.pow_level = pow_level
        self.cur_level = cur_level
        self.p_low_lim = p_low_lim
        self.p_high_lim = p_high_lim
        self.op_mode = op_mode

        if self.comms_on == "OFF":
            response = self.serialmessage(isHSHAKE)
            if response == 'OFF':
                self.serialsend(self.turnON(HSHAKE))
        else:
            self.comms_on = 'ON'
        """else:
            self.comms = 'OFF'
"""

        if self.wlength == wlength:
            self.wlength = self.serialmessage(isWLENGTH)

        if self.pow_level == pow_level:
            self.pow_level = self.serialmessage(isOUTPOWLEVEL)

        if self.cur_level == cur_level:
            self.cur_level = self.serialmessage(isOUTCURLEVEL)

        if self.p_low_lim == p_low_lim:
            self.p_low_lim = self.serialmessage(isPOWLOWLIM)

        if self.p_high_lim == p_high_lim:
            self.p_high_lim = self.serialmessage(isPOWHIGHLIM)

        if self.op_mode == op_mode:
            self.op_mode = self.serialmessage(isLASOPMODE)

    def __str__(self):
        return f"Laser: Comms = {self.comms_on}, laser on ={self.is_on}, wavelength = {self.wlength}, power level = {self.power_level},\
                current = {self.cur_level}, Power lower limit = {self.p_low_lim}, Power High Limit = {self.p_high_lim}"

    def turnON(self, pycommand):
        """
        Switches the property specified in pycommand ON

        :param pycommand: a python-translated SCPI command
        :return:
        """
        if pycommand[-1] == '?':
          command = (pycommand[:-1] + " ON")
        else:
            command = (pycommand + ' ON')
        self.serialsend(command)
        #self.serialread() # added this otherwise the next .serialmessage will return a bit of garbage (specifically 'OK\r\n)
        self.is_on = "ON"

    def turnOFF(self, pycommand):
        """
        Switches the property specified in pycommand OFF

        :param pycommand: a python-translated SCPI command
        :return:
        """
        if pycommand[-1] == '?':
            command = (pycommand[:-1] + " OFF")
        else:
            command = (pycommand + ' OFF')
        self.serialsend(command)
        #self.serialread()
        self.is_on = "OFF"

    def set_power(self, power, keep_in_cwp = True):
        """
            Alternative power setting method: Sets laser power level. 
            If keep_in_cwp=True, remains in CWP mode.
            If keep_in_cwp=False, captures stabilized operating current and applies it to CWC mode.
            """
        # Ensure laser is in Constant Power mode to adjust optical output
        if self.op_mode != "CWP":
            self.serialmessage(LASOPMODEINTCWP)
            self.op_mode = "CWP"


        # Send power setpoint
        message = f"{LASPOWLEVEL} {power}"
        self.serialmessage(message)

        # Stabilization loop using absolute tolerance
        tolerance = 5e-4
        timeout = 10.0
        start_time = time.time()

        while True:
            system_output = float(self.serialmessage(isOUTPOWLEVEL))
            if abs(system_output - power) <= tolerance:
                break
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Laser power failed to stabilize within {timeout}s")
            time.sleep(0.5)

        self.pow_level = system_output
        self.cur_level = float(self.serialmessage(isOUTCURLEVEL))

        if not keep_in_cwp:
            # Transfer operating current to CWC setpoint before switching modes
            self.serialmessage(f"{LASCURLEVEL} {self.cur_level}")
            self.serialmessage(LASOPMODEINTCWC)
            self.op_mode = self.serialmessage(isLASOPMODE)

    @synchronized_method
    def get_all_status(self):
        status = {}
        status['current'] = self.serialmessage(isOUTCURLEVEL)
        status['power_preset'] = self.serialmessage(isLASPOWLEVEL)
        status['power'] = self.serialmessage(isOUTPOWLEVEL)
        status['wlength'] = self.wlength
        status['comms'] = self.serialmessage(isHSHAKE)
        status['is_on'] = self.is_on
        return status

    """def show(self):
        self.show()"""


