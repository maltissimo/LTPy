from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QVBoxLayout, QPushButton
import sys, os

class DirectorySelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.button = QPushButton('Select Directory', self)
        self.button.clicked.connect(self.select_directory)

        layout.addWidget(self.button)
        self.setLayout(layout)

    def select_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly

        QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            os.path.expanduser("~"),
            options=options
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DirectorySelector()
    ex.show()
    sys.exit(app.exec_())