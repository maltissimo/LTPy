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
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.setCentralWidget(self.console)
        self.setWindowTitle("PyQt Console Output")
        self.resize(800, 400)

        # Output something to test
        print("Welcome to the PyQt Console!")
        for i in range(10):
            print(f"Line {i}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create console and redirect BEFORE creating main window
    console = ConsoleWidget()
    sys.stdout = console
    sys.stderr = console

    window = MainWindow(console)
    window.show()
    sys.exit(app.exec_())