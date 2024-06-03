"""
Contains all the info necessary for the communication between Mainc Computer (MC) and Laser (L)
The Coherent Vendor ID of the USB laser is
3405

the ProductId is
59

This can be checked with:

import usb.core
devices = usb.core.find(find_all= True)
for device in devices:
    print(f"Vendor ID: ", (device.idVendor), "Product ID: ", (device.idProduct)

or via lsusb

from the command line.

Main communication is via pyserial, through USB. The USB is connected to MC on the ttyACM0 port
Info on OBIS Manual, part 3/

"""
import pyserial
import time

PORT = "ttyACM0" # /dev/ttyACM0 port over which the OBIS is connnected to MC
ENDL = "\r\n"   # end of communication , carriage return + new line
BAUD = 9600 # Baudrate for the communication


class SerialConn(serial.Serial):
    """
    Models a connection throug the pyserial interface from the MC to the OBIS remote.
    """
    def __init__(self, port = None, baudrate = None, lastcommand, lastouput ):
        super():__init__(port = PORT, baudrate = BAUD,
                         bytesize = serial.EIGHTBITS,
                         parity = serial.PARITY_NONE,
                         stopbits = serial.STOPBITS_ONE,
                         timeout = 1,
                         xonxoff = False,
                         rtscts = False,
                         dsrdtr = False,
                         inter_byte_timeout = None,
                         write_timeout = 2
                         )
        self.lastcommand = None
        self.lastoutput = None

    def serialsend (self, data):
        """
        Writes a string into the serial pipe, and updates the lastcommand of the SerialConn object,
        so as one can keep track of what happens

        :param data: string to be written
        :return:
        """
        command = str(data) + ENDL
        self.write(command.encode('ascii'))
        self.lastcommand = command

       """
       this below should go in usage, not in this method.
        try: 
            command = str(data) + ENDL
            self.write(command.encode('ascii'))
        except serial.SerialException as e: 
            print(f"SerialException: error writing to serial port: {e}")
        except Exception as e:
            print(f"Exception: an unexpected error occurred : {e}")
        """

    def serialread(self):
        """
        Reads the output from the serial, updates the lastoutput property of the SerialConn object,
        so one can keep track of what is happening.
        :param self:
        :return: output, a string for usage
        """

        output = self.read_all().decode('ascii').strip()
        self.lastoutput = output

        return(output)

    def serialmessage(self, data):

        self.serialread(data)
        answer = self.serialread()

        return(answer)

