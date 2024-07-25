# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox
import sys, os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from src.API.base import QtRequest

from src.tools.tools import find_project_file,find_color,get_system_info,createPop



# Rest of the code remains the same
class reject_From(QWidget):

    closed = pyqtSignal()  # 自定义信号

    def __init__(self, isClose=False):
        super(reject_From, self).__init__()
        self.version = "v2.8.1"
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.isClose = isClose
        self.setupUi(self)

    def setupUi(self, Form):
        self._from = Form
        Form.setObjectName("Form")
        Form.resize(400, 220)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 20, 359, 24))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(30, 70, 341, 31))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(40, 130, 311, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        # 禁止窗体 放大缩小
        Form.setFixedSize(400, 220)
        # 禁用窗体最大化
        Form.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        # 禁用窗体最小化
        Form.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, False)
        if self.isClose:
            # 禁用关闭按钮
            Form.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, False)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        # 增加 获取CDK 的插槽事件
        self.pushButton_2.clicked.connect(self.getCDK)
        # 增加 激活 的插槽事件
        self.pushButton.clicked.connect(self.activate)
        # 设置窗口 icon
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(
                find_project_file(
                    os.path.normpath(
                        os.path.join(
                            os.path.join(os.path.expanduser("~"), "ChickenBrothers"),
                            "public/head.ico",
                        )
                    )
                )
            ),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        Form.setWindowIcon(icon)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "激活设备/增加时间"))
        self.label.setText(_translate("Form", "激活设备"))
        self.pushButton.setText(_translate("Form", "激活"))
        self.pushButton_2.setText(_translate("Form", "获取CDK"))
        # 禁用关闭按钮

    def getCDK(self):
        image_path = "xxxx"  # Replace with the actual path to your image
        # createPop(image_path)

    # 激活卡密
    def activate(self):
        # 检查激活框
        km_id = self.lineEdit.text()
        if not km_id:
            QMessageBox.warning(self, "错误", "未填写卡密")
            return
        window_id = get_system_info()
        if not window_id:
            QMessageBox.warning(self, "错误", "无法获取机器码")
            return
        # 激活
        try:
            km_id = km_id.strip()
            _, res = QtRequest(
                url=f"/activate_card/{km_id}?windows_id={window_id}",
                method="PUT",
            )
            print(res)
            if res.get("code") == 0:
                if res.get("message") == "卡密已被使用":
                    QMessageBox.warning(self, "错误", "卡密已被使用")
                    return
                else:
                    QMessageBox.information(self, "成功", res.get("message"))
                    self._from.close()
            else:
                QMessageBox.warning(self, "错误", res.get("message"))
                pass
        except Exception as e:
            QMessageBox.warning(self, "错误", "未知错误")

    def closeEvent(self, event):
        self.closed.emit()  # 发射信号
        super(reject_From, self).closeEvent(event)


class reject_From_noModel(QWidget):
    def __init__(self):
        super(reject_From_noModel, self).__init__()
        self.setupUi(self)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 220)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 20, 359, 24))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(30, 70, 341, 31))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(40, 130, 311, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        # 禁止窗体 放大缩小
        Form.setFixedSize(400, 220)
        # 禁用窗体最大化
        Form.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        # 禁用窗体最小化
        Form.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, False)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        # 增加 获取CDK 的插槽事件
        self.pushButton_2.clicked.connect(self.getCDK)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "激活设备/增加时间"))
        self.label.setText(_translate("Form", "激活设备"))
        self.pushButton.setText(_translate("Form", "激活"))
        self.pushButton_2.setText(_translate("Form", "获取CDK"))

    def getCDK(self):
        image_path = "xxxx"  # Replace with the actual path to your image
        # createPop(image_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = reject_From_noModel()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
