
import paramiko
import time
import threading
from ControlCenter.MultiThreading import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from PyQt5.QtCore import pyqtSignal, QObject

"""
Contains all the info necessary for the communication between Main Computer (MC) and the Gantry's Pmac (G)
    See the LTPy.mdj file for class basic design

Author M. Altissimo c/o Elettra Sincrotrone Trieste SCpA
"""

GPASCII = "gpascii -2"  # this is needed to start the interpreter on the Pmac, i.e. to init the Pmac
EOT = "\x04"  # End of transmission character, to close connection to the PMAC. the SSH stays open. Equivalent to pass CTRL+C
ACK = "\x06"  # ACKNOWLEDGE character, see https://donsnotes.com/tech/charsets/ascii.html.
delim = "\r\n"
right = "STDIN Open for ASCII Input"

class Pmac_Shell():
    """
    Object modeling the connection to the Pmac as an interactive shell. Main methods:

    Open ssh connection to G
    Close ssh connection to G
    Initialize Pmac
    Send messages to G
    Receive messages from G
    Checks connection status

    """
    def __init__(self, ssh = None, pmac_shell = None, pmac_ip = "127.0.0.1", username = "", password = "", alive = False, nbytes = 1024, rawoutput = None, textoutput = "No output from the shell!"):
        """
        Inits some attributes. The initial IP is set to be the loobpack interface. Username and password are attributes
        that  must be user defined.
        """
        super().__init__()
        self.ssh = ssh if ssh else paramiko.SSHClient() # an object accessing the SSHClient methods
        self.pmac_shell = pmac_shell  # initialized as none
        self.pmac_ip = pmac_ip  # the loopback interface
        #print("Inside PMAC shell,IP: ", self.pmac_ip)
        self.username = username
        #print("Inside PMAC shell, username: ", self.username)
        self.password = password
       # print("Inside PMAC shell, password: ", self.password)
        self.alive = alive #setting the connection status as False
        self.nbytes = nbytes # nr of bites for the receiver function
        self.rawoutput = rawoutput # Initialize the output bytes buffer string as None
        self.textoutput = textoutput

        #Multithreading facilities

        self.worker = WorkerThread(task = self.receive_message, sleep_time = 100)
        self.worker.begin_signal.connect(self.send_message)
        self.worker.update_signal.connect(self.store_message)
        self.worker.error_signal.connect(self.handleworkererror)
        self.worker.end_signal.connect(self.worker_stop)



    def worker_stop(self):
        self.worker.stop()

    def openssh(self):
        """
           This functions connects to PMAC, setting the pmac_shell attribute to a shell of ssh class (ssh.invoke_shell())
           The ip is set to be the loopback interface by default, username and password are dummy values as well.
           The correct values must be passed to the method by the caller

           :return pmac_shell: a shell from paramiko, that can be used to send commands down.
        , ssh = None, pmac_ip = None, username = None,password = None

        self.ssh = ssh
        self.pmac_ip = pmac_ip
        self.username = username
        self.password = password
        """
        # Load SSH host keys.
        try:
            self.ssh.load_system_host_keys()
            # Add SSH host key when missing.
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.ssh.connect(self.pmac_ip, username = self.username, password = self.password)

            self.pmac_shell = self.ssh.invoke_shell()
            self.pmac_shell.setblocking(0)
            if self.ssh.get_transport() and self.ssh.get_transport().is_active():
                self.alive = True
            else:
                self.alive = False
                raise ConnectionError ("SSH connection established,but transport is not active")

        except paramiko.AuthenticationException:
            self.alive = False
            conn_error = myWarningBox(title = "Error!",
                                      message = "Incorrect authentication credentials")
            conn_error.show_warning()
        except paramiko.SSHException as e:
            self.alive = False
            ssh_error = myWarningBox(title = "Error!",
                                     message = str(e))
            ssh_error.show_warning()
        except Exception as e:
            self.alive = False
            ex_error = myWarningBox(title = "Error!",
                                    message = str(e))

    def close_connection(self):
        """
        this closes the connection to the Pmac, setting alive to False. Checks if the conection is to the PMAC or not, in order to send the correct "close" commannd.

        :return:

        """
        if self.username == "root":
            self.send_message(EOT) # sends the End of Transmission character sequence as specified above the class
        else:
            self.send_message("exit")

        self.pmac_shell.close()
        self.alive = False

    def send_message(self, message = ""):
        """
        Sends a message down to the Pmac. Message must end with a new line character, otherwise they will not be executed
        on the remote host. So in case anyone forgets, a \n is added here if message doesn't end with it.

       :param shell: a shell connection to the Pmac
       :param message: a string containing the message to be sent the Pmac
       """
        if self.alive:
            if not message.endswith("\n"):
                message = message + "\n"
            self.pmac_shell.send(message)
            message = ''
        else:
           conn_error = myWarningBox(title = "Error! ",
                                     message = "Connection not active")
           conn_error.show_warning()

    def receive_message(self):
        """
          Sets the textoutput property of self as an array of strings.
          Depending on the command before, the relevant output is
          self.textoutput[-2] after a pmac_init
          self.textoutput[-1] after any other command.
          """
        try:
            if self.pmac_shell.recv_ready():
                try:
                    self.rawoutput = self.pmac_shell.recv(self.nbytes).decode("ascii")
                    outlines = self.rawoutput.split(delim)
                    self.worker.update_signal.emit(outlines)
                    return outlines
                except socket.timeout:
                    print("Socket timeout occurred during recv, continuing...")
                    return []
            else:
                return []
        except Exception as e:
            pass
            #print(f"Unexpected error in receive_message: {e}")
            return []

    def store_message(self,message):
        self.textoutput = []
        self.textoutput = message

    def handleworkererror(self, emessage):
        worker_err = myWarningBox(title = "Error!",
                                  message = emessage)
        worker_err.show_warning()

    def start_receiving(self):
        self.worker.start()


    def is_open(self):
        """
       Checks if the connection is alive or not
       Uses the get_transport() function to gain access to the Transport members in paramiko, returning True if the connection is active
        This throws an error if the connection is not active, so careful, hence the method

       """

        if not self.alive == self.pmac_shell.get_transport().is_active():
            self.alive = False


class Gantry(Pmac_Shell):

    """
    This object describes a connection to the Gantry. It contains functions to initialize the communication properly, and to
    set echo to off (see details in the function header).
    """

    def __init__(self, pmac_ip="127.0.0.1", username="", password="", alive=False, nbytes=1024, echo=None,
                 isinit=False):
        super().__init__(pmac_ip=pmac_ip, username=username, password=password, alive=alive, nbytes=nbytes)
        self.echo = echo  # this has to be checked and initialized to the value on the PMAC. Must be 1 to avoid echoing of command issued to PMAC
        self.isinit = isinit # Set to False for safety reasons.

    def __str__(self):
        """"
        this should give all the info to the factory class in Control Center.
        """
        return f"Gantry: IP = {self.pmac_ip}, username = {self.username}, password = {self.password}, alive = {self.alive}, echo = {self.echo}, isinit = {self.isinit}"

    def send_receive(self, message):

        """This function compounds the send_message and the simple_output methods of the Pmac_Shell class. This function is
        to be used ONLY with an open SSH on a PMAC terminal, as it will otherwise produce unintellegible outputs.

        :param message: a string containing the message to be set to the PMAC
        :return: a string output"""

        if self.alive:
            self.start_receiving()
            self.send_message(message) # this sends the message down to the SSH connection
            #print(message)
            #self.receive_message()
            start_time = time.time()
            time.sleep(0.051) # this is  a critical parameter!! the function doesn't work if it's 0.05, so careful.

            while True:
                if self.pmac_shell.recv_ready():
                    self.store_message(self.receive_message())
                    break
                if time.time() - start_time >0.51:
                    return "timeout"
            self.worker_stop()
            return (self.textoutput[1]) if self.textoutput else "No response"
        else:
            #self.worker.stop()
            return("Connection not active")

    def pmac_init(self):
        """
        Initializes the Pmac with the proper string, defined above the Gantry_Connection class.

        :return:
        """
        #print(GPASCII)
        self.send_message(GPASCII)
        time.sleep(0.2)
        self.receive_message()
        #print(self.textoutput)
        response = self.textoutput[-2]
        if response == right:
            self.isinit = True
            return(response)
        else:
            return(response)

    def set_echo(self):
        """
        this function checks on the PMAC if echo is on or off. If echo is on, then:
        issue:      echo
        return:     0

            issue:      motor[x].actpos
            return:     Motor[x].ActPos=xxx.xyz

        If echo is off:
        issue:      echo
        return:     1

        issue:      motor[x].actpos
        return:    xxx.xyz

        See page 1154 of PMAC software manual.
        So it's importanto to check if it's off, and in case it's not, set it to 1

        :return:
        """

        echo_response = self.send_receive("echo\n")
        if echo_response == str(0):
            self.send_receive("echo 1\n")
            self.echo = str(1)
        else:
            self.echo = str(1)

    def status(self):
        """
        A controller method to check for shell status from other classes..
        :return:
        """
        message = ("Shell status:  " + str(self.alive) + "\n" +
              "Shell init status: " + str(self.isinit))

        return(message)

