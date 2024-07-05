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


It is  assumed here that, since the transfer is 9600 bps, the waiting time must be no less than 70ms, otherwise the
answers comes back either empty or garbled.
"""
import serial, serial.tools.list_ports

import time

PORT = "/dev/ttyACM0" # /dev/ttyACM0 port over which the OBIS is connnected to MC
ENDL = "\r\n"   # end of communication , carriage return + new line
BAUD = 9600 # Baudrate for the communication


class SerialConn(serial.Serial):
    """
    Models a connection throug the pyserial interface from the MC to the OBIS remote.
    """
    def __init__(self, port = None, baudrate = None, lastcommand = None, lastouput = None):
        super().__init__(port = PORT, baudrate = BAUD,
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
        # self.reset_input_buffer()
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
        self.lastoutput = None
        out = self.read_all().decode('ascii').strip()
        output = out[:-3]
        self.lastoutput = output.strip()

        return(output.strip())

    def serialmessage(self, data):

        self.serialsend(data)
        time.sleep(0.07)

        return(self.serialread())







