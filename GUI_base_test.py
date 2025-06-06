# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from Graphics.Base_Classes_graphics.BaseClasses import MyGroupBox, MyLabel, MyPushButton, MyTextBrowser, MyTextEdit

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        MainWindow.setFont(font)
        MainWindow.setWindowTitle("LTPy main Window")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(640, 10, 1280, 720))
        self.tabWidget.setObjectName("tabWidget")
        self.slopes_meas = QtWidgets.QWidget()
        self.slopes_meas.setObjectName("slopes_meas")
        self.tabWidget.addTab(self.slopes_meas, "")
        self.heights_meas = QtWidgets.QWidget()
        self.heights_meas.setObjectName("heights_meas")
        self.tabWidget.addTab(self.heights_meas, "")
        self.cam_view = QtWidgets.QWidget()
        self.cam_view.setObjectName("cam_view")
        self.tabWidget.addTab(self.cam_view, "")
        self.ControlCenter = QtWidgets.QTabWidget(self.centralwidget)
        self.ControlCenter.setGeometry(QtCore.QRect(0, 10, 640, 720))
        self.ControlCenter.setObjectName("ControlCenter")
        self.Motor_control = QtWidgets.QWidget()
        self.Motor_control.setObjectName("Motor_control")
        self.ControlCenter.addTab(self.Motor_control, "")
        self.cam_control = QtWidgets.QWidget()
        self.cam_control.setObjectName("cam_control")
        self.ControlCenter.addTab(self.cam_control, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.ControlCenter.addTab(self.tab, "")
        self.MotorBox = MyGroupBox(self.centralwidget)
        self.MotorBox.setGeometry(QtCore.QRect(0, 740, 384, 216))
        self.MotorBox.setMinimumSize(QtCore.QSize(384, 216))
        """    
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.MotorBox.setFont(font)
        """

        self.MotorBox.setTitle("Motor Positions")
        self.MotorBox.setObjectName("MotorBox")
        self.x_label = MyLabel(self.MotorBox)
        self.x_label.setGeometry(QtCore.QRect(10, 40, 60, 16))
        self.x_label.setObjectName("x_label")
        self.x_display = MyTextBrowser(self.MotorBox)
        self.x_display.setGeometry(QtCore.QRect(80, 40, 80, 20))
        self.x_display.setMinimumSize(QtCore.QSize(80, 20))
        self.x_display.setObjectName("x_display")
        self.x_units = MyLabel(self.MotorBox)
        self.x_units.setGeometry(QtCore.QRect(170, 40, 60, 16))
        self.x_units.setObjectName("x_units")
        self.y_label = MyLabel(self.MotorBox)
        self.y_label.setGeometry(QtCore.QRect(10, 60, 60, 16))
        self.y_label.setObjectName("y_label")
        self.z_label = MyLabel(self.MotorBox)
        self.z_label.setGeometry(QtCore.QRect(10, 80, 60, 16))
        self.z_label.setObjectName("z_label")
        self.pitch_label = MyLabel(self.MotorBox)
        self.pitch_label.setGeometry(QtCore.QRect(10, 100, 60, 16))
        self.pitch_label.setObjectName("pitch_label")
        self.roll_label = MyLabel(self.MotorBox)
        self.roll_label.setGeometry(QtCore.QRect(10, 120, 60, 16))
        self.roll_label.setObjectName("roll_label")
        self.yaw_label = MyLabel(self.MotorBox)
        self.yaw_label.setGeometry(QtCore.QRect(10, 140, 60, 16))
        self.yaw_label.setObjectName("yaw_label")
        self.y_display = MyTextBrowser(self.MotorBox)
        self.y_display.setGeometry(QtCore.QRect(80, 60, 80, 20))
        self.y_display.setMinimumSize(QtCore.QSize(80, 20))
        self.y_display.setObjectName("y_display")
        self.y_units = MyLabel(self.MotorBox)
        self.y_units.setGeometry(QtCore.QRect(170, 60, 60, 16))
        self.y_units.setObjectName("y_units")
        self.z_units = MyLabel(self.MotorBox)
        self.z_units.setGeometry(QtCore.QRect(170, 80, 60, 16))
        self.z_units.setObjectName("z_units")
        self.z_display = MyTextBrowser(self.MotorBox)
        self.z_display.setGeometry(QtCore.QRect(80, 80, 80, 20))
        self.z_display.setMinimumSize(QtCore.QSize(80, 20))
        self.z_display.setObjectName("z_display")
        self.pitch_display = MyTextBrowser(self.MotorBox)
        self.pitch_display.setGeometry(QtCore.QRect(80, 100, 80, 20))
        self.pitch_display.setMinimumSize(QtCore.QSize(80, 20))
        self.pitch_display.setObjectName("pitch_display")
        self.roll_display = MyTextBrowser(self.MotorBox)
        self.roll_display.setGeometry(QtCore.QRect(80, 120, 80, 20))
        self.roll_display.setMinimumSize(QtCore.QSize(80, 20))
        self.roll_display.setObjectName("roll_display")
        self.yaw_display = MyTextBrowser(self.MotorBox)
        self.yaw_display.setGeometry(QtCore.QRect(80, 140, 80, 20))
        self.yaw_display.setMinimumSize(QtCore.QSize(80, 20))
        self.yaw_display.setObjectName("yaw_display")
        self.pitch_units = MyLabel(self.MotorBox)
        self.pitch_units.setGeometry(QtCore.QRect(170, 100, 60, 16))
        self.pitch_units.setObjectName("pitch_units")
        self.roll_units = MyLabel(self.MotorBox)
        self.roll_units.setGeometry(QtCore.QRect(170, 120, 60, 16))
        self.roll_units.setObjectName("roll_units")
        self.yaw_units = MyLabel(self.MotorBox)
        self.yaw_units.setGeometry(QtCore.QRect(170, 140, 60, 16))
        self.yaw_units.setObjectName("yaw_units")
        self.savepos_button = MyPushButton(self.MotorBox)
        self.savepos_button.setGeometry(QtCore.QRect(250, 40, 113, 32))
        self.savepos_button.setObjectName("savepos_button")
        self.MeasBox = MyGroupBox(self.centralwidget)
        self.MeasBox.setGeometry(QtCore.QRect(390, 740, 384, 216))
        self.MeasBox.setMinimumSize(QtCore.QSize(384, 216))

        """font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.MeasBox.setFont(font)
        """


        self.MeasBox.setTitle("Measurement setup")
        self.MeasBox.setObjectName("MeasBox")
        self.meas_length = MyLabel(self.MeasBox)
        self.meas_length.setGeometry(QtCore.QRect(10, 50, 80, 20))
        self.meas_length.setObjectName("meas_length")
        self.meas_stepsize = MyLabel(self.MeasBox)
        self.meas_stepsize.setGeometry(QtCore.QRect(10, 70, 80, 20))
        self.meas_stepsize.setObjectName("meas_stepsize")
        self.meas_units = MyLabel(self.MeasBox)
        self.meas_units.setGeometry(QtCore.QRect(200, 50, 80, 20))
        self.meas_units.setObjectName("meas_units")
        self.label_4 = MyLabel(self.MeasBox)
        self.label_4.setGeometry(QtCore.QRect(200, 70, 80, 20))
        self.label_4.setObjectName("label_4")
        self.meas_stepsize_2 = MyLabel(self.MeasBox)
        self.meas_stepsize_2.setGeometry(QtCore.QRect(10, 90, 80, 20))
        self.meas_stepsize_2.setObjectName("meas_stepsize_2")
        self.label_5 = MyLabel(self.MeasBox)
        self.label_5.setGeometry(QtCore.QRect(200, 90, 80, 20))
        self.label_5.setObjectName("label_5")
        self.length_input = MyTextEdit(self.MeasBox)
        self.length_input.setGeometry(QtCore.QRect(100, 50, 80, 20))
        self.length_input.setObjectName("length_input")
        self.ss_input = MyTextEdit(self.MeasBox)
        self.ss_input.setGeometry(QtCore.QRect(100, 70, 80, 20))
        self.ss_input.setObjectName("ss_input")
        self.textEdit_3 = MyTextEdit(self.MeasBox)
        self.textEdit_3.setGeometry(QtCore.QRect(100, 90, 80, 20))
        self.textEdit_3.setObjectName("textEdit_3")
        self.start_meas = MyPushButton(self.MeasBox)
        self.start_meas.setGeometry(QtCore.QRect(0, 140, 160, 32))
        self.start_meas.setObjectName("start_meas")
        self.stop_meas = MyPushButton(self.MeasBox)
        self.stop_meas.setGeometry(QtCore.QRect(220, 140, 160, 32))
        self.stop_meas.setObjectName("stop_meas")
        self.PosBox = MyGroupBox(self.centralwidget)
        self.PosBox.setGeometry(QtCore.QRect(780, 740, 384, 216))
        self.PosBox.setMinimumSize(QtCore.QSize(384, 216))
        """ 
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.PosBox.setFont(font)"""
        self.PosBox.setTitle("Stored positions")
        self.PosBox.setObjectName("PosBox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 24))
        self.menubar.setObjectName("menubar")
        self.menuLTP_Main_Window = QtWidgets.QMenu(self.menubar)
        self.menuLTP_Main_Window.setObjectName("menuLTP_Main_Window")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuLTP_Main_Window.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.ControlCenter.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.slopes_meas), _translate("MainWindow", "Slopes measurements"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.heights_meas), _translate("MainWindow", "Heights measurements"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cam_view), _translate("MainWindow", "Camera view"))
        self.ControlCenter.setTabText(self.ControlCenter.indexOf(self.Motor_control), _translate("MainWindow", "Motor Control"))
        self.ControlCenter.setTabText(self.ControlCenter.indexOf(self.cam_control), _translate("MainWindow", "Camera Control"))
        self.ControlCenter.setTabText(self.ControlCenter.indexOf(self.tab), _translate("MainWindow", "Laser Control"))
        self.x_label.setText(_translate("MainWindow", "X motor"))
        self.x_units.setText(_translate("MainWindow", "µm"))
        self.y_label.setText(_translate("MainWindow", "Y motor"))
        self.z_label.setText(_translate("MainWindow", "Z motor"))
        self.pitch_label.setText(_translate("MainWindow", "Pitch"))
        self.roll_label.setText(_translate("MainWindow", "Roll"))
        self.yaw_label.setText(_translate("MainWindow", "Yaw"))
        self.y_units.setText(_translate("MainWindow", "µm"))
        self.z_units.setText(_translate("MainWindow", "µm"))
        self.pitch_units.setText(_translate("MainWindow", "Degrees"))
        self.roll_units.setText(_translate("MainWindow", "Degrees"))
        self.yaw_units.setText(_translate("MainWindow", "Degrees"))
        self.savepos_button.setText(_translate("MainWindow", "Save Position"))
        self.meas_length.setText(_translate("MainWindow", "Length"))
        self.meas_stepsize.setText(_translate("MainWindow", "Step size"))
        self.meas_units.setText(_translate("MainWindow", "mm"))
        self.label_4.setText(_translate("MainWindow", "mm"))
        self.meas_stepsize_2.setText(_translate("MainWindow", "Nr of points"))
        self.label_5.setText(_translate("MainWindow", "#"))
        self.start_meas.setText(_translate("MainWindow", "Start measurement"))
        self.stop_meas.setText(_translate("MainWindow", "STOP!"))
        self.menuLTP_Main_Window.setTitle(_translate("MainWindow", "LTP Main Window"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
