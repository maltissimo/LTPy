# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CameraViewer_UI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets

from Graphics.Base_Classes_graphics.BaseClasses import MyQLineEdit, MyPushButton


class Ui_PylonCamViewer(object):
    def setupUi(self, PylonCamViewer):
        PylonCamViewer.setObjectName("PylonCamViewer")
        PylonCamViewer.resize(1018, 811)
        PylonCamViewer.setWindowTitle("Pylon Camera Viewer")
        PylonCamViewer.setToolTip("")
        PylonCamViewer.setStatusTip("")
        PylonCamViewer.setWhatsThis("")
        PylonCamViewer.setAccessibleName("")
        self.centralwidget = QtWidgets.QWidget(PylonCamViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.CamViewer = QtWidgets.QFrame(self.centralwidget)
        self.CamViewer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.CamViewer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CamViewer.setObjectName("CamViewer")
        self.verticalLayout.addWidget(self.CamViewer)
        self.ButtonsFrame = QtWidgets.QFrame(self.centralwidget)
        self.ButtonsFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ButtonsFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ButtonsFrame.setObjectName("ButtonsFrame")
        self.frame = QtWidgets.QFrame(self.ButtonsFrame)
        self.frame.setGeometry(QtCore.QRect(-10, 0, 411, 111))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.StartGrab = MyPushButton(self.frame)
        self.StartGrab.setObjectName("StartGrab")
        self.gridLayout.addWidget(self.StartGrab, 2, 0, 1, 1)
        self.StopGrab = MyPushButton(self.frame)
        self.StopGrab.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.StopGrab.setObjectName("StopGrab")
        self.gridLayout.addWidget(self.StopGrab, 3, 0, 1, 1)
        self.SetAcqTime = MyPushButton(self.frame)
        self.SetAcqTime.setObjectName("SetAcqTime")
        self.gridLayout.addWidget(self.SetAcqTime, 2, 2, 1, 1)
        self.AcqTLineEdit = MyQLineEdit(self.frame)
        self.AcqTLineEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.AcqTLineEdit.setText("")
        self.AcqTLineEdit.setObjectName("AcqTLineEdit")
        self.gridLayout.addWidget(self.AcqTLineEdit, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 2)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.verticalLayout.addWidget(self.ButtonsFrame)
        self.verticalLayout.setStretch(0, 6)
        self.verticalLayout.setStretch(1, 1)
        PylonCamViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PylonCamViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1018, 24))
        self.menubar.setObjectName("menubar")
        PylonCamViewer.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(PylonCamViewer)
        self.statusbar.setObjectName("statusbar")
        PylonCamViewer.setStatusBar(self.statusbar)

        self.retranslateUi(PylonCamViewer)
        QtCore.QMetaObject.connectSlotsByName(PylonCamViewer)

    def retranslateUi(self, PylonCamViewer):
        _translate = QtCore.QCoreApplication.translate
        self.StartGrab.setText(_translate("PylonCamViewer", "Grab"))
        self.StopGrab.setText(_translate("PylonCamViewer", "Stop Grabbing"))
        self.SetAcqTime.setText(_translate("PylonCamViewer", "Set"))
        self.label.setText(_translate("PylonCamViewer", "Exposure Time (µs)"))