import socket
import time
import threading
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox

ACK = b"\x06"
delim = "\r\n"
right = "STDIN Open for ASCII Input"


class Pmac_Shell:
    """
    Drop-in TCP replacement for the SSH Pmac_Shell.
    Connects directly to the Power PMAC ASCII server on TCP port 1025.
    """

    def __init__(self, pmac_ip="127.0.0.1", port=1025, timeout=2.0, nbytes=4096,
                 username="", password="", alive=False, rawoutput=None, textoutput="No output"):
        self.pmac_ip = pmac_ip
        self.port = port
        self.timeout = timeout
        self.nbytes = nbytes
        self.username = username
        self.password = password
        self.alive = False
        self.rawoutput = rawoutput
        self.textoutput = textoutput
        self.sock = None
        self.lock = threading.Lock()
        self.isinit = False

        # Connect automatically if a non-loopback IP is specified, or connect() can be called manually
        if self.pmac_ip != "127.0.0.1":
            self.connect()

    def connect(self):
        """Establishes persistent TCP connection to Power PMAC ASCII server and synchronizes."""
        with self.lock:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.timeout)
                self.sock.connect((self.pmac_ip, self.port))

                # Flush banner by sending a newline or command to trigger the ACK delimiter
                self.sock.sendall(b"\n")

                buffer = bytearray()
                while True:
                    chunk = self.sock.recv(self.nbytes)
                    if not chunk:
                        raise ConnectionResetError("Socket closed prematurely by PMAC.")
                    buffer.extend(chunk)
                    if ACK in chunk:
                        break

                self.alive = True
                self.isinit = True
            except Exception as e:
                self.alive = False
                self.isinit = False
                if self.sock:
                    try:
                        self.sock.close()
                    except Exception:
                        pass
                    self.sock = None
                print(f"TCP connect failed: {e}")

    def openssh(self):
        """Alias kept for backward compatibility with existing LTPy callers."""
        self.connect()

    def close_connection(self):
        """Closes the active TCP socket."""
        with self.lock:
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                except Exception:
                    pass
                finally:
                    self.sock = None
            self.alive = False

    def is_open(self):
        """Checks if the connection is currently open."""
        return self.alive and (self.sock is not None)

    def flush_channel(self):
        """Clears out any stale bytes or lingering ACKs from the TCP receive buffer."""
        if not self.alive or not self.sock:
            return
        try:
            self.sock.setblocking(False)
            while True:
                data = self.sock.recv(self.nbytes)
                if not data:
                    break
        except (BlockingIOError, socket.error):
            pass
        finally:
            if self.sock:
                self.sock.settimeout(self.timeout)

    def send_message(self, message=""):
        """
        Sends an asynchronous command line to the PMAC without waiting for return data.
        Ensures proper newline termination.
        """
        with self.lock:
            if not self.alive or not self.sock:
                return
            if not message.endswith("\n"):
                message += "\n"
            try:
                self.sock.sendall(message.encode("ascii"))
            except Exception as e:
                print(f"[PMAC Send Error] {e}")
                self.alive = False


class Gantry(Pmac_Shell):
    """
    Main controller class for Gantry communications over TCP.
    """

    def __init__(self, pmac_ip="127.0.0.1", port=1025, timeout=2.0, username="",
                 password="", alive=False, nbytes=4096, echo=None, isinit=False):
        super().__init__(pmac_ip=pmac_ip, port=port, timeout=timeout, username=username,
                         password=password, alive=alive, nbytes=nbytes)
        self.echo = echo
        self.isinit = isinit

    def __str__(self):
        return (f"Gantry: IP = {self.pmac_ip}:{self.port}, alive = {self.alive}, "
                f"echo = {self.echo}, isinit = {self.isinit}")

    def pmac_init(self):
        """
        Port 1025 connects straight to the native command interpreter.
        Initializes communication state and sets echo mode.
        """
        if not self.alive:
            return "Connection not active."

        with self.lock:
            self.flush_channel()
            self.isinit = True
            return right

    def send_receive(self, message, timeout=2.0):
        """
        Sends a command and reads incoming chunks until the ACK (0x06) delimiter arrives.
        Populates self.rawoutput and self.textoutput identically to legacy SSH methods.
        """
        if not self.alive or not self.sock:
            return "Connection not active"

        with self.lock:
            try:
                self.flush_channel()

                if not message.endswith("\n"):
                    message += "\n"

                self.sock.sendall(message.encode("ascii"))

                buffer = bytearray()
                self.sock.settimeout(timeout)

                while True:
                    chunk = self.sock.recv(self.nbytes)
                    if not chunk:
                        self.alive = False
                        return "Connection closed by PMAC"
                    buffer.extend(chunk)
                    if ACK in chunk:
                        break

                # Strip out ACK delimiter and decode
                clean_payload = buffer.replace(ACK, b"").decode("ascii", errors="ignore").strip()

                self.rawoutput = clean_payload
                # Emulate legacy split behavior expected by Motor/CompMotor
                self.textoutput = clean_payload.split(delim)

                if clean_payload:
                    # In TCP mode without shell echo, the answer is usually clean_payload itself
                    return clean_payload
                return ""

            except socket.timeout:
                self.textoutput = []
                return "timeout"
            except Exception as e:
                print(f"[PMAC Comms Error] {e}")
                self.alive = False
                return "error"

    def set_echo(self):
        """
        Checks echo status on PMAC and forces echo = 1 (off) so queries return pure values.
        """
        echo_response = self.send_receive("echo\n")
        if echo_response.strip() == "0":
            self.send_receive("echo 1\n")
        self.echo = "1"

    def status(self):
        return f"Shell status: {self.alive}\nShell init status: {self.isinit}"