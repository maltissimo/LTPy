from Hardware.obis_commands import *
from Communication.MCL import *


class Laser (SerialConn):
    def __init__(self, comms_on = "OFF", is_on = 'OFF', wlength = 0.0, pow_level = None, cur_level = None, p_low_lim = None, p_high_lim = None):
        super().__init__()
        self.comms_on = comms_on
        self.is_on = self.serialmessage(isLASON)
        self.wlength = wlength
        self.pow_level = pow_level
        self.cur_level = cur_level
        self.p_low_lim = p_low_lim
        self.p_high_lim = p_high_lim

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

    def set_power(self, power):
        """
        Sets the power level to a user-defined value. Updates the self.pow_level and self.cur_level in the object accordingly

        :param power: preset value of laser power,
        :return:
        """
        original_power = self.serialmessage(isLASPOWLEVEL) # just checking the presets.
        pow = ' ' + str(power) # makes a string with a space for setting the power
        message = LASPOWLEVEL + pow # this is the complete message to be sent to the laser
        self.serialmessage(message) # message sent
        system_output = self.serialmessage(isOUTPOWLEVEL)
        #print(f"system_output: {system_output}")  # Debugging
        #print(f"power level: {self.pow_level}")
        #print("difference output - pow_level: ", float(system_output.strip()) - float(self.pow_level.strip()))
        if abs(float(system_output.strip()) - float(self.pow_level.strip())) <3e-6:
            self.pow_level = system_output
            self.cur_level = self.serialmessage(isOUTCURLEVEL)

        else:
            self.pow_level = original_power # better leave it unchanged

    def show(self):
        self.show()


