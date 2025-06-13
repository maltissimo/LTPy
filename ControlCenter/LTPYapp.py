from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow
from ControlCenter.MultiThreading import WorkerThread
from ControlCenter.Control_Utilities import console_welcome
from PyQt5.QtCore import QObject, pyqtSignal
from ControlCenter.MeasurementControls import *
from PyQt5.QtCore import QObject, pyqtSignal


#####################Console code#####################
class ConsoleStream(QObject):
    new_text = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self._buffer = ""

    def write(self, text):
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self.new_text.emit(line + "\n")

    def flush(self):
        if self._buffer:
            self.new_text.emit(self._buffer)
            self._buffer = ""
        # Required for sys.stdout compatibility

class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("background-color: white; color: black; font-family: Consolas, monospace;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def append_text(self, text):
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)

    def clear_console(self):
        self.setPlainText("")

##################### Main App #####################
class MainLTPApp:
    def __init__(self):
        self.PMAC_credentials = None

        self.PMAC_credentials = self.PMAC_connector()
        """print(self.PMAC_credentials["ip"])
        print(self.PMAC_credentials["username"])
        print(self.PMAC_credentials["password"])"""

        if not self.PMAC_credentials:
            cred_warning = myWarningBox("Connection issues", "Connection initialization Cancelled")
            cred_warning.show_warning()
            return

        print(self.PMAC_credentials)

        try:
            self.manager = SSHConnectionManager.get_instance(self.PMAC_credentials)
        except Exception as e:
            conn_warning = myWarningBox(title = "Conn error", message = str({e}))
            conn_warning.show_warning()
            return
        shared_connection = self.manager.get_connection()

        self.motor_controls = MotorControls(shared_connection)
        self.laser = LaserControl()
        self.controls = MeasurementControls(shell = shared_connection,
                                            motors = self.motor_controls)

    def PMAC_connector(self):
        conn_initer = Connection_initer()
        credentials = conn_initer.get_credentials()
        if credentials is None:
            return None
        return credentials

    def run(self):
        self.laser.show()
        self.motor_controls.show()
        self.controls.show()

#####################Main App Entry#####################

if __name__ == "__main__":
    app = QApplication([])

    console_window = QMainWindow()
    console_widget = ConsoleWidget()
    console_stream = ConsoleStream()

    console_stream.new_text.connect(console_widget.append_text)

    sys.stdout = console_stream
    sys.stderr = console_stream

    console_window.setCentralWidget(console_widget)
    console_window.setWindowTitle("LTPy output console")
    console_window.resize(800, 200)
    console_window.move(100, 800)
    console_window.show()
    print(console_welcome())

    main_app = MainLTPApp()
    main_app.run()
    app.exec_()  # Event loop for PyQt
