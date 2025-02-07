# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CameraViewer_UI.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets

from Graphics.Base_Classes_graphics.BaseClasses import *

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
        self.ButtonsFrame = QtWidgets.QFrame(self.CamViewer)
        self.ButtonsFrame.setGeometry(QtCore.QRect(0, 640, 1000, 106))
        self.ButtonsFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ButtonsFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ButtonsFrame.setObjectName("ButtonsFrame")
        self.frame = QtWidgets.QFrame(self.ButtonsFrame)
        self.frame.setGeometry(QtCore.QRect(-10, 0, 411, 111))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(15, -1, 15, -1)
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
        self.frame_2 = QtWidgets.QFrame(self.ButtonsFrame)
        self.frame_2.setGeometry(QtCore.QRect(400, 0, 601, 111))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.widget = QtWidgets.QWidget(self.frame_2)
        self.widget.setGeometry(QtCore.QRect(1, 0, 591, 111))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.FWHM_horizontalLayout = QtWidgets.QHBoxLayout()
        self.FWHM_horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.FWHM_horizontalLayout.setSpacing(10)
        self.FWHM_horizontalLayout.setObjectName("FWHM_horizontalLayout")
        self.FWHM_gridLayout = QtWidgets.QGridLayout()
        self.FWHM_gridLayout.setObjectName("FWHM_gridLayout")
        self.FWHMY_display = MyLabel(self.widget)
        self.FWHMY_display.setObjectName("FWHMY_display")
        self.FWHM_gridLayout.addWidget(self.FWHMY_display, 3, 1, 1, 1)
        self.FWHMX_display = MyLabel(self.widget)
        self.FWHMX_display.setObjectName("FWHMX_display")
        self.FWHM_gridLayout.addWidget(self.FWHMX_display, 1, 1, 1, 1)
        self.FWHMY_label = MyLabel(self.widget)
        self.FWHMY_label.setText("")
        self.FWHMY_label.setObjectName("FWHMY_label")
        self.FWHM_gridLayout.addWidget(self.FWHMY_label, 3, 2, 1, 1)
        self.FWHMX_label = MyLabel(self.widget)
        self.FWHMX_label.setText("")
        self.FWHMX_label.setObjectName("FWHMX_label")
        self.FWHM_gridLayout.addWidget(self.FWHMX_label, 1, 2, 1, 1)
        self.FWHM_horizontalLayout.addLayout(self.FWHM_gridLayout)
        self.FWHM_checkBox = QtWidgets.QCheckBox(self.widget)
        self.FWHM_checkBox.setObjectName("FWHM_checkBox")
        self.FWHM_horizontalLayout.addWidget(self.FWHM_checkBox)
        self.FWHM_horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.addLayout(self.FWHM_horizontalLayout)
        self.centroid_horizontalLayout = QtWidgets.QHBoxLayout()
        self.centroid_horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.centroid_horizontalLayout.setSpacing(10)
        self.centroid_horizontalLayout.setObjectName("centroid_horizontalLayout")
        self.centroid_gridLayout = QtWidgets.QGridLayout()
        self.centroid_gridLayout.setObjectName("centroid_gridLayout")
        self.centroidY_display = MyLabel(self.widget)
        self.centroidY_display.setObjectName("centroidY_display")
        self.centroid_gridLayout.addWidget(self.centroidY_display, 3, 1, 1, 1)
        self.centroidX_display = MyLabel(self.widget)
        self.centroidX_display.setObjectName("centroidX_display")
        self.centroid_gridLayout.addWidget(self.centroidX_display, 1, 1, 1, 1)
        self.centroidY_label = MyLabel(self.widget)
        self.centroidY_label.setText("")
        self.centroidY_label.setObjectName("centroidY_label")
        self.centroid_gridLayout.addWidget(self.centroidY_label, 3, 2, 1, 1)
        self.centroidX_label = MyLabel(self.widget)
        self.centroidX_label.setText("")
        self.centroidX_label.setObjectName("centroidX_label")
        self.centroid_gridLayout.addWidget(self.centroidX_label, 1, 2, 1, 1)
        self.centroid_horizontalLayout.addLayout(self.centroid_gridLayout)
        self.centroid_checkBox = QtWidgets.QCheckBox(self.widget)
        self.centroid_checkBox.setObjectName("centroid_checkBox")
        self.centroid_horizontalLayout.addWidget(self.centroid_checkBox)
        self.centroid_horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.addLayout(self.centroid_horizontalLayout)
        self.verticalLayout.addWidget(self.CamViewer)
        PylonCamViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PylonCamViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1018, 22))
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
        self.FWHMY_display.setText(_translate("PylonCamViewer", "FWHM Y (um)"))
        self.FWHMX_display.setText(_translate("PylonCamViewer", "FWHM X (um)"))
        self.FWHM_checkBox.setText(_translate("PylonCamViewer", "Show FWHM"))
        self.centroidY_display.setText(_translate("PylonCamViewer", "Centroid Y"))
        self.centroidX_display.setText(_translate("PylonCamViewer", "Centroid X"))
        self.centroid_checkBox.setText(_translate("PylonCamViewer", "Show Centroid"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PylonCamViewer = QtWidgets.QMainWindow()
    ui = Ui_PylonCamViewer()
    ui.setupUi(PylonCamViewer)
    PylonCamViewer.show()
    sys.exit(app.exec_())
