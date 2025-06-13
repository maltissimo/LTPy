import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow
from ControlCenter.MultiThreading import WorkerThread
from ControlCenter.Control_Utilities import console_welcome

from PyQt5.QtCore import QObject, pyqtSignal

class ConsoleStream(QObject):
    new_text = pyqtSignal(str)

    def write(self, text):
        if text.strip():  # Skip empty lines
            self.new_text.emit(str(text))

    def flush(self):
        pass  # Required for sys.stdout compatibility

class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)
            self.setLineWrapMode(QPlainTextEdit.NoWrap)
            self.setStyleSheet("background-color: black; color: white; font-family: Consolas, monospace;")
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        def append_text(self, text):
            self.insertPlainText(text)
            self.moveCursor(QTextCursor.End)

        def clear_console(self):
            self.setPlainText("")

class MainWindow(QMainWindow):
    def __init__(self, console, console_stream):
        super().__init__()
        self.console = console
        self.setCentralWidget(self.console)
        self.setWindowTitle("LTPy output console")
        self.resize(800, 200)
        # Connect stream signal to console display
        console_stream.new_text.connect(self.console.append_text)

        # Example worker thread
        self.worker = WorkerThread(task=self.background_task, sleep_time=500)
        self.worker.start()

        # Output something to test
    def background_task(self):
        print(console_welcome())
        return

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    console = ConsoleWidget()
    console_stream = ConsoleStream()

    # Redirect stdout and stderr to the console stream
    sys.stdout = console_stream
    sys.stderr = console_stream

    window = MainWindow(console, console_stream)
    window.show()

    sys.exit(app.exec_())