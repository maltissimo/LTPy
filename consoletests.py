import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow


class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("background-color: black; color: white; font-family: Consolas, monospace;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.buffer = []

        # Periodically flush the buffer to the text area
        self.flush_timer = QTimer()
        self.flush_timer.timeout.connect(self.flush_buffer)
        self.flush_timer.start(100)  # milliseconds

    def write(self, text):
        self.buffer.append(text)

    def flush_buffer(self):
        if self.buffer:
            self.insertPlainText("".join(self.buffer))
            self.buffer.clear()
            self.moveCursor(QTextCursor.End)

    def flush(self):
        # Optional for compatibility with sys.stdout
        pass

    def clear_console(self):
        self.setPlainText("")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.console = ConsoleWidget()
        self.setCentralWidget(self.console)

        # Redirect stdout and stderr
        sys.stdout = self.console
        sys.stderr = self.console

        print("Welcome to the PyQt Console!")
        for i in range(10):
            print(f"Line {i}")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())