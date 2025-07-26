from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow
from ControlCenter.MultiThreading import WorkerThread
from ControlCenter.Control_Utilities import console_welcome
from PyQt5.QtCore import QObject, pyqtSignal
from ControlCenter.MeasurementControls import *
from PyQt5.QtCore import QObject, pyqtSignal
from Hardware.Detector import Camera
from Graphics.Base_Classes_graphics.MainLTPyApp_GUI import Ui_LTPy


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
##################### LTPy startup window #####################
class LTPyStartupWindow(QMainWindow):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.ui = Ui_LTPy()
        self.ui.setupUi(self)

        # Buttons connections:
        self.ui.MeasurementButton.clicked.connect(self.show_measurement_controls)
        self.ui.StabMeasurement.clicked.connect(self.show_stability_measurement)
        self.ui.LaserButton.clicked.connect(self.show_laser_controls)
        self.ui.MotorsButton.clicked.connect(self.show_motor_controls)
        self.ui.QuitButton.clicked.connect(self.quit_application)

        self.setWindowTitle("LTPy - Widget Launcher")

    def show_measurement_controls(self):
        if hasattr(self.main_app, "controls") and self.main_app.controls:
            self.main_app.controls.show()
            self.show_laser_controls(self)
            self.show_motor_controls(self)
            self.main_app.raise_()
            #self.main_app.activateWindow()
        else:
            print("Measurement controls not initialized")

    def show_stability_measurement(self):
        pass
        """
        passing for the minute
        if hasattr(self.main_app, "stability_meas"):
            self.main_app.stability_meassurement.show()
        else:
            pass"""
    def show_laser_controls(self):
        if hasattr(self.main_app, "laser") and self.main_app.laser:
            self.main_app.laser.show()
            self.main_app.laser.raise_()
            #self.main_app.activateWindow()
        else:
            print("Laser controls not initialized")

    def show_motor_controls(self):
        if hasattr (self.main_app, "motor_controls") and self.main_app.motor_controls:
            self.main_app.motor_controls.show()
            self.main_app.motor_controls.raise_()
            #self.main_app.motor_controls.activateWindow()
        else:
            print("Motor controls not initialized")

    def quit_application(self):
        reply = QMessageBox.question(
            self, "Exit Confirmation",
            "Are you sure you want to quit LTPy?\nThis will close all control windows.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.main_app.cleanup_and_quit()
        ##################### Main App #####################
class MainLTPApp:
    def __init__(self):
        self.PMAC_credentials = None
        self.motor_controls = None
        self.laser = None
        self.controls = None
        self.camera_controls = None
        self.stability_meas = None
        self.startup_window = None

        self.PMAC_credentials = self.PMAC_connector()
        """print(self.PMAC_credentials["ip"])
        print(self.PMAC_credentials["username"])
        print(self.PMAC_credentials["password"])"""

        if not self.PMAC_credentials:
            cred_warning = myWarningBox("Connection issues", "Connection initialization Cancelled")
            cred_warning.show_warning()
            return

        print("Correct PMAC Credentials, connecting...")

        try:
            self.manager = SSHConnectionManager.get_instance(self.PMAC_credentials)
            shared_connection = self.manager.get_connection()


        except Exception as e:
            conn_warning = myWarningBox(title = "Conn error", message = str({e}))
            conn_warning.show_warning()
            return

        camera = Camera()
        self.startup_window = LTPyStartupWindow(self)
        self.initialize_controls(shared_connection, camera)

    def initialize_controls(self, shared_connection, camera):
        try:
            print("Initializing controls...")
            self.motor_controls = MotorControls(shell = shared_connection)
            print()
            print("Motor Controls Initialized")

            self.laser = LaserControl()
            print()
            print("Laser Controls Initialized")

            self.controls = MeasurementControls(shell = shared_connection,
                                                motors = self.motor_controls, detector = camera)
            print()
            print("Measurement Controls Initialized")

            self.camera_controls = CamViewer(detector= camera)
            print()
            print("Camera Controls Initialized")

            self.stability_meas = StabilityMeasurement()
            print()
            print("Stability Measurement Initialized")

        except Exception as e:
            error_msg = f"Error initializing controls: {str(e)}"
            print(error_msg)
            error_warning = myWarningBox(title="Initialization Error", message=error_msg)
            error_warning.show_warning()

    def run(self):
        if self.startup_window:
            self.startup_window.show()
        else:
            print("Startup window not initialized")

    def cleanup_and_quit(self):
        print("Cleaning up and quitting...")
        if self.motor_controls:
            self.motor_controls.close()
        if self.laser:
            self.laser.close()
        if self.controls:
            self.controls.close()
        if self.camera_controls:
            self.camera_controls.close()
        if self.stability_meas:
            self.stability_meas.close()
        if self.startup_window:
            self.startup_window.close()
        print("Cleanup complete. Exiting...")

        QApplication.quit()


    def PMAC_connector(self):
        conn_initer = Connection_initer()
        credentials = conn_initer.get_credentials()
        if credentials is None:
            return None
        return credentials

    """def run(self):
        self.laser.show()
        self.motor_controls.show()
        self.controls.show()"""

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
    if main_app.startup_window:
        main_app.run()
        sys.exit(app.exec_())  # Event loop for PyQt
    else:
        print("Application not initialized")
        sys.exit(1)
