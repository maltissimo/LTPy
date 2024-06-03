import obis_helpers as oh
from MCL import *


class Laser (SerialConn):
    def __init__(self, comms_on = False, is_on = False, wlength = 0.0, pow_level = 0.0, cur_level = 0.0):
        self.comms = self.serialmessage(oh.isLASON)

