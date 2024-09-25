from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextEdit, QTextBrowser, QLabel, QPushButton, QGroupBox, QWidget, QLineEdit, QComboBox
from PyQt5.QtWidgets import QVBoxLayout

# General values:
WIDTH = 80
HEIGHT = 20
FONT = "Arial"
FONTSIZE = 14
QBOXWIDTH = 384
QBOXHEIGHT = 216


class MainWindow(object):
    def setupUi(self, Motors):
        Motors.setObjectName("CHANGE MY NAME")
        Motors.resize(640, 480)
        Motors.setWindowTitle("MainWindow")
        Motors.setToolTip("")
        Motors.setStatusTip("")
        Motors.setWhatsThis("")
        Motors.setAccessibleName("")
        self.centralwidget = QtWidgets.QWidget(Motors)
        self.centralwidget.setObjectName("centralwidget")
        Motors.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Motors)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 24))
        self.menubar.setObjectName("menubar")
        Motors.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Motors)
        self.statusbar.setObjectName("statusbar")
        Motors.setStatusBar(self.statusbar)

        self.retranslateUi(Motors)
        QtCore.QMetaObject.connectSlotsByName(Motors)

    def retranslateUi(self, Motors):
        pass

class MySubWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Title")

        layout = QVBoxLayout()
        label = MyLabel("This is my sub window")
        layout.addWidget(label)
        self.setLayout(layout)


class MyTextEdit(QTextEdit):
    enter_pressed = pyqtSignal()

    def __init__(self, parent = None, width = WIDTH, height = HEIGHT):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.enter_pressed.connect(self.on_enter_pressed)
        self.initialize()
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def initialize(self):

        self.setMaximumSize(QSize(160, 20))
        self.setSizeIncrement(QSize(5, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)
        #self.setInputMethodHints(Qt.ImhNone)
        self.setPlainText(u"")

    def get_dimensions(self):
        return (self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)

    def on_enter_pressed(self):
        text = self.toPlainText()
        return(text)

class MyLabel(QLabel):

    def __init__(self, parent = None, width = WIDTH, height = HEIGHT):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.initialize()
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def initialize(self):
        self.setMaximumSize(QSize(160, 20))
        self.setSizeIncrement(QSize(5, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)
        #self.setPlainText(u"")

    def get_dimensions(self):

        return(self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

"""class MyTextEdit(QTextEdit):

    def __init__(self, parent = None, width = WIDTH, height = HEIGHT ):
        super().__init__(parent)
        self.setFixedSize(width, height)

    def initialize(self):
        self.setMaximumSize(QSize(160, 20))
        self.setSizeIncrement(QSize(5, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)
        self.setPlainText(u"")
        #if QT_config(statustip)
        self.setStatusTip(u"")
        # endif // QT_config(statustip)
        #if QT_config(whatsthis)
        self.setWhatsThis(u"")
        #endif //QT_config(statustip)
        #if QT_config(accessibility)
        self.setAccessibleName(u"")
        #endif // QT_config(accessibility)
        self.setInputMethodHints(Qt.ImhPreferNumbers)

    def get_dimensions(self):
        return (self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.handle_enter_key()
        else:
            super().keyPressEvent(event)
    
    def get_text(self):"""


class MyPushButton(QPushButton):
    def __init__(self, parent = None, width =  1.5 * WIDTH, height = 1.6 * HEIGHT):
        super().__init__(parent)
        self.setFixedSize(width, height)
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def initialize(self):
        self.setMaximumSize(QSize(240, 40))
        self.setSizeIncrement(QSize(5,2))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)
        self.setPlainText(u"")
        # if QT_config(statustip)
        self.setStatusTip(u"")
        # endif // QT_config(statustip)
        # if QT_config(whatsthis)
        self.setWhatsThis(u"")
        # endif //QT_config(statustip)
        # if QT_config(accessibility)
        self.setAccessibleName(u"")
        # endif // QT_config(accessibility
        #if QT_config(shortcut)
        self.setShortcut(u"")
        #endif // QT_config(shortcut)

    def get_dimensions(self):
        return (self.width(), self.height())


    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

class MyTextBrowser(QTextBrowser):

    def __init__(self, parent = None, width = WIDTH, height = HEIGHT):
        super().__init__(parent)
        self.setFixedSize(width, height)
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.initialize()

    def initialize(self):

        self.setMaximumSize(QSize(160, 20))
        self.setSizeIncrement(QSize(5, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)
        self.setPlainText(u"")

    def get_dimensions(self):
        return (self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

    def updateValue(self, value):
        self.setText(str(value))


class MyGroupBox(QGroupBox):
    def __init__(self, parent = None, width = QBOXWIDTH, height = QBOXHEIGHT):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def initialize(self):
        self.setMaximumSize(width, height)
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.setFont(font)
        self.setPlainText(u"")

    def get_dimensions(self):
        return (self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

class MyQLineEdit(QLineEdit):
    def __init__(self, parent = None, width = WIDTH, height = HEIGHT):
        super().__init__(parent)
        self.setFixedSize(width, height)
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.initialize()

    def initialize(self):

        self.setMaximumSize(QSize(160, 20))
        self.setSizeIncrement(QSize(5, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)


    def get_dimensions(self):
        return (self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

class MyComboBox(QComboBox):
    def __init__(self, parent = None, width = 2 * WIDTH, height = HEIGHT):
        super().__init__(parent)
        self.setFixedSize(width, height)
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.initialize()

    def initialize(self):

        self.setMaximumSize(QSize(160, 20))
        self.setSizeIncrement(QSize(5, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)


    def get_dimensions(self):
        return (self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

class MyIndicator(QLabel):
    def __init__(self, parent = None, width = 32, height = 32):
        super().__init__(parent)
        self.setFixedSize(width, height)
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.initialize()

    def initialize(self):

        self.setMaximumSize(QSize(32, 32))
        self.setSizeIncrement(QSize(0, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)
        self.setStyleSheet(("QLabel {bacground-color: red; color: white;"))


    def get_dimensions(self):
        return (self.width(), self.height())

    def setGeometry(self, rect):
        # Ensure a minimum width and height
        rect.setWidth(max(rect.width(), self.width()))
        rect.setHeight(max(rect.height(), self.height()))
        super().setGeometry(rect)

    def turn_green(self):
        self.setStyleSheet(("QLabel {bacground-color: green;"))

    def turn_red(self):
        self.setStyleSheet(("QLabel {bacground-color: red;"))

class UnitsLabel(QLabel):
    """ this is now showing only for µm and degrees. It can be expanded to add other units. """

    def __init__(self, value_list, parent = None, width = WIDTH, height = HEIGHT):
        super().__init__(parent)
        self.value_list = value_list
        self.setFixedSize(width, height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.initialize()

    def initialize(self):
        self.setMaximumSize(QSize(160, 20))
        self.setSizeIncrement(QSize(0, 0))
        font = QFont()
        font.setFamily(FONT)
        font.setPointSize(FONTSIZE)
        self.setFont(font)

    def update_value(self, index):
        if 0 <= index <=2:
            self.setText("µm")
        elif 2 < index <=5:
            self.setText("degrees")
        else:
            self.setText("")
