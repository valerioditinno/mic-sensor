# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(526, 373)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.file_id_input_layout = QtWidgets.QHBoxLayout()
        self.file_id_input_layout.setObjectName("file_id_input_layout")
        self.label_file_id = QtWidgets.QLabel(self.centralwidget)
        self.label_file_id.setObjectName("label_file_id")
        self.file_id_input_layout.addWidget(self.label_file_id)
        self.edit_file_id = QtWidgets.QLineEdit(self.centralwidget)
        self.edit_file_id.setObjectName("edit_file_id")
        self.file_id_input_layout.addWidget(self.edit_file_id)
        self.verticalLayout.addLayout(self.file_id_input_layout)
        self.snr_input_layout = QtWidgets.QHBoxLayout()
        self.snr_input_layout.setObjectName("snr_input_layout")
        self.label_snr = QtWidgets.QLabel(self.centralwidget)
        self.label_snr.setObjectName("label_snr")
        self.snr_input_layout.addWidget(self.label_snr)
        self.edit_snr = QtWidgets.QLineEdit(self.centralwidget)
        self.edit_snr.setObjectName("edit_snr")
        self.snr_input_layout.addWidget(self.edit_snr)
        self.verticalLayout.addLayout(self.snr_input_layout)
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout.addWidget(self.progress_bar)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        self.btn_stop = QtWidgets.QPushButton(self.centralwidget)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setObjectName("btn_stop")
        self.buttons_layout.addWidget(self.btn_stop)
        self.btn_start = QtWidgets.QPushButton(self.centralwidget)
        self.btn_start.setObjectName("btn_start")
        self.buttons_layout.addWidget(self.btn_start)
        self.verticalLayout.addLayout(self.buttons_layout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Simulation"))
        self.label_file_id.setText(_translate("MainWindow", "File ID"))
        self.label_snr.setText(_translate("MainWindow", "SNR"))
        self.btn_stop.setText(_translate("MainWindow", "Stop"))
        self.btn_start.setText(_translate("MainWindow", "Start"))

