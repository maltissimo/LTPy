import datetime
from Hardware import Source, Detector, Motors
from Communication import MCG, MCL

TODAY = datetime.datetime.now()

class Measurement():
    def __init__(self, xmove = xmove, xmotor = xmotor, xpos= None, date = None, saved_data = None):


    def move_next_pos(self):
        pass
    def take_cmos_image(self):
        pass
    def centroid_calc(self):
        pass
    def save_data(self):
        pass
