
import paramiko
import time

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
        self.ssh = ssh if ssh else paramiko.SSHClient() # an object accessing the SSHClient methods
        self.pmac_shell = pmac_shell  # initialized as none
        self.pmac_ip = pmac_ip  # the loopback interface
        print("Inside PMAC shell,IP: ", self.pmac_ip)
        self.username = username
        print("Inside PMAC shell, username: ", self.username)
        self.password = password
        print("Inside PMAC shell, password: ", self.password)
        self.alive = alive #setting the connection status as False
        self.nbytes = nbytes # nr of bites for the receiver function
        self.rawoutput = rawoutput # Initialize the output bytes buffer string as None
        self.textoutput = textoutput

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
        self.ssh.load_system_host_keys()
        # Add SSH host key when missing.
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # credentials = get_credentials()
        self.ssh.connect(self.pmac_ip, username = self.username, password = self.password)
        #print("Successfully connected to ", credentials[0])
        pmac_shell = self.ssh.invoke_shell()
        if pmac_shell.get_transport().is_active():
            self.pmac_shell = pmac_shell
            self.alive = True
        else:
            self.alive = False
            return("Connection not active!!")
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
        if not message.endswith("\n"):
            message = message + "\n"

        self.pmac_shell.send(message)
    def receive_message(self):
        """
       sets the textouput property of self as an array of strings.
       Depending on the command before, the relevant output is
       self.textoutput[-2] after a pmac_init
       self.textoutput[-3] after any other command.

        :return:
        """
        self.textoutput = []
        if self.pmac_shell.recv_ready():
            self.rawoutput = self.pmac_shell.recv(self.nbytes).decode("ascii")
            outlines= self.rawoutput.split(delim)
            self.textoutput.extend(outlines)
        else:
            self.textoutput = ("Something went wrong with the connection")

        #print(self.textoutput)
    def is_open(self):
        """s
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

    def __init__(self,  pmac_ip = "127.0.0.1", username = "", password = "", alive = False, nbytes = 1024, echo = None, isinit = False):
        super().__init__(pmac_ip = pmac_ip, username = username, password = password, alive = alive, nbytes = nbytes )
        self.echo = echo  # this has to be checked and initialized to the value on the PMAC. Must be 1 to avoid echoing of command issued to PMAC
        self.isinit = isinit # Set to False for safety reasons.

    def __str__(self):
        """"
        this should give all the info to the factory class in Control Center.
        """
        return f"Gantry: IP = {self.pmac_ip}, username = {self.username}, password = {self.password}, alive = {self.alive}, echo = {self.echo}, isinit = {self.isinit}"

    def send_receive(self, message):
        """
        This function compounds the send_message and the simple_output methods of the Pmac_Shell class. This function is
        to be used ONLY with an open SSH on a PMAC terminal, as it will otherwise produce unintellegible outputs.

        :param message: a string containing the message to be set to the PMAC
        :return: a string output
        """
        if self.alive is not False:
            self.send_message(message) # this sends the message down to the SSH connection
            time.sleep(0.015)
            self.receive_message()
            alan = self.textoutput[1]

            return (str(alan))

            """output = self.simple_output()
            return(output)"""

        else:
            return("Connection not active")

    def pmac_init(self):
        """
        Initializes the Pmac with the proper string, defined above the Gantry_Connection class.

        :return:
        """
        self.send_message(GPASCII)
        time.sleep(0.2) # this is needed in order for the data to be transmitted and read.
        self.receive_message()
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

        echo0 = self.send_receive("echo\n")
        if echo0 == str(0):
            echo0 = self.send_receive("echo 1\n")
            self.echo = str(1)
        else:
            self.echo = str(0)

    def status(self):
        """
        A controller method to check for shell status from other classes..
        :return:
        """
        message = ("Shell status: ", self.alive,
              "\nShell init status: ", self.isinit)

        return(message)


"""
if __name__ == "__main__":
    main()
"""
