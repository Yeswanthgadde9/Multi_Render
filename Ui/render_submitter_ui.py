# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'render_submitter.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1061, 327)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setStyleSheet("QPushButton:pressed {\n"
                                        "background-color: #FFA53F;\n"
                                        "}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_10.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setStyleSheet("QPushButton:pressed {\n"
                                      "background-color: #FFA53F;\n"
                                      "}")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_10.addWidget(self.pushButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_10, 2, 0, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gridLayout_2.addLayout(self.verticalLayout_4, 1, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setStyleSheet("QPushButton:pressed {\n"
                                        "background-color: #FFA53F;\n"
                                        "}")
        self.pushButton_3.setMinimumSize(QtCore.QSize(250, 0))
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setStyleSheet("QPushButton:pressed {\n"
                                        "background-color: #FFA53F;\n"
                                        "}")
        self.pushButton_4.setMinimumSize(QtCore.QSize(250, 0))
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        self.tableWidget.horizontalHeaderItem(0).setToolTip('Name of the Write Node')
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.horizontalHeaderItem(1).setToolTip('Set the Render Frame Range')
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeaderItem(2).setToolTip('Choose the Channels that you want to render'
                                                            ' set to rgb by default')
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.horizontalHeaderItem(3).setToolTip('Render Order is set automatically')
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.tableWidget.horizontalHeaderItem(4).setToolTip('Status of your Render')
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.tableWidget.horizontalHeaderItem(5).setToolTip('An option to Create Read Node after render')
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        #self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Multi Render"))
        self.pushButton_2.setText(_translate("Form", "Render"))
        self.pushButton.setText(_translate("Form", "Cancel"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Node"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Frame Range"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Channels"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Render Order"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("Form", "Status"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("Form", "After Render"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("Form", "Progress"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("Form", "Cancel Render"))
        self.pushButton_3.setText(_translate("Form", "Update"))
        self.pushButton_4.setText(_translate("Form", "Create Read"))
