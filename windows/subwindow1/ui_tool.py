# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tool.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(418, 301)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_num = QtWidgets.QLabel(self.centralwidget)
        self.label_num.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_num.setAlignment(QtCore.Qt.AlignCenter)
        self.label_num.setObjectName("label_num")
        self.verticalLayout.addWidget(self.label_num)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_num = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_num.setObjectName("lineEdit_num")
        self.horizontalLayout.addWidget(self.lineEdit_num)
        self.slider_num = QtWidgets.QSlider(self.centralwidget)
        self.slider_num.setProperty("value", 0)
        self.slider_num.setSliderPosition(0)
        self.slider_num.setTracking(True)
        self.slider_num.setOrientation(QtCore.Qt.Horizontal)
        self.slider_num.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.slider_num.setTickInterval(0)
        self.slider_num.setObjectName("slider_num")
        self.horizontalLayout.addWidget(self.slider_num)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.Button_reset = QtWidgets.QPushButton(self.centralwidget)
        self.Button_reset.setObjectName("Button_reset")
        self.verticalLayout.addWidget(self.Button_reset)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 3)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 418, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.toolBar)
        self.action = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/src/start.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action.setIcon(icon)
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/src/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_2.setIcon(icon1)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/src/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_3.setIcon(icon2)
        self.action_3.setObjectName("action_3")
        self.toolBar.addAction(self.action)
        self.toolBar.addAction(self.action_2)
        self.toolBar.addAction(self.action_3)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_num.setText(_translate("MainWindow", "TextLabel"))
        self.lineEdit_num.setText(_translate("MainWindow", "0"))
        self.Button_reset.setText(_translate("MainWindow", "reset"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.action.setText(_translate("MainWindow", "开始"))
        self.action_2.setText(_translate("MainWindow", "运行"))
        self.action_3.setText(_translate("MainWindow", "编译"))
import src_rc
