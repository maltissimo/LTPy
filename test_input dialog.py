import sys

from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
class MainWindos(QWidget):
    def __init__(self):
        super().__init__()
        self.ip = None
        self.username = None
        self.password = None

        self.get_credentials()

    def get_credentials(self):
        ip, ok = QInputDialog.getText(self, "PMAC Credentials", "Enter PMAC IP address: ")
        if ok:
            self.ip = ip

        username, ok = QInputDialog.getText(self, "PMAC Credentials", "Enter PMAC Username: ")
        if ok:
            self.username = username

        self.password, ok = self.password_dialog()

    def password_dialog(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("PMAC Credentials")

        layout = QVBoxLayout()

        label = QLabel("Enter PMAC Password: ")
        layout.addWidget(label)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(button_box)

        dialog.setLayout(layout)


        if dialog.exec_() == QInputDialog.Accepted:
            return password_input.text(), True
        else:
            return None, False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindos()
    window.show()
    sys.exit(app.exec_())
