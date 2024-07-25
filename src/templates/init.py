from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import QTimer, QProcess, pyqtSignal

from src.API.base import QtRequest
from src.templates.reject import reject_From
import ctypes, win32gui, subprocess, os
import src.tools.tools as mytools
from src.templates.window import window_Form
import requests, zipfile

from src.tools.tools import find_project_file, find_color, get_system_info,determine_quadrant_and_distance_with_tolerance



class MySignalClass(QtCore.QObject):
    # 定义一个信号
    valueChanged = pyqtSignal(int)


class MySignalClass2(QtCore.QObject):
    # 定义一个信号
    valueChanged = pyqtSignal(str)


class init_Form(QWidget):

    def __init__(self):
        super(init_Form, self).__init__()
        self.version = "v2.8.1"
        self.setupUi(self)
        QTimer.singleShot(200, self.on_window_shown)

    def setupUi(self, Form):
        self._from = Form
        Form.setObjectName("Form")
        Form.resize(454, 215)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(0, 60, 454, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(110, 100, 241, 31))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        # 禁止窗体 放大缩小
        Form.setFixedSize(454, 215)
        # 禁用窗体最大化
        Form.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        # 禁用窗体最小化
        Form.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, False)
        self.retranslateUi(Form)
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
        # 创建信号类实例
        self.signal_emitter = MySignalClass()
        # 连接信号到槽函数
        self.signal_emitter.valueChanged.connect(self.updateProgressBar)
        self.updatelabels = MySignalClass2()
        self.updatelabels.valueChanged.connect(self.label.setText)
        # self.on_window_shown()
        # QTimer.singleShot(1, self.on_window_shown)

    def updateProgressBar(self, value):
        # 槽函数，更新进度条的值
        self.progressBar.setValue(value)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "吃鸡兄弟-预检查"))
        self.label.setText(_translate("Form", "预检查"))
        # 设置 self.label 的宽度为百分百
        self.label.setFixedWidth(454)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def on_window_shown(self):
        # 检查redis是否开启 且 可以连接
        if self.redisState():
            self.signal_emitter.valueChanged.emit(20)
        else:
            self._from.close()
            return
        # 检查Windows屏幕分辨率
        if self.check_windows_resolution():
            self.signal_emitter.valueChanged.emit(40)
        else:
            self._from.close()
            return
        # 检查设备与网络连接
        # if self.check_connectivity():
        #     self.signal_emitter.valueChanged.emit(50)
        # else:
        #     self._from.close()
        #     return
        # # 检查图片资源是否存在
        # if self.loading_images():
        #     self.signal_emitter.valueChanged.emit(80)
        # else:
        #     self._from.close()
        #     return
        # # 检查ocr
        # if self.check_ocr_new():
        #     self.signal_emitter.valueChanged.emit(100)
        # else:
        #     self._from.close()
        #     return
        # 都通过后 展示主窗体
        self.window_Form = window_Form()
        self._from.close()
        self.window_Form.show()

    # 检查Windows屏幕分辨率
    def check_windows_resolution(self):
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        # print(width, height)
        return True
        _width = 3840
        _height = 2160
        _width = 1920
        _height = 1080
        # 如果主屏幕分辨率 不是 1920 * 1080 的话 弹出弹窗 提示 分辨率错误
        if width != _width or height != _height:
            QMessageBox.warning(
                self, "错误", f"请将屏幕分辨率设置为 {_width} * {_height}"
            )
            self._from.close()
            return False
        else:
            return True

    # 检查游戏是否开启
    def check_game_open(self):
        hwnd = win32gui.FindWindow(None, "TslGame")
        if hwnd == 0:
            QMessageBox.warning(self, "错误", "请先开启游戏！")
            # ctypes.windll.user32.MessageBoxW(0, "请先开启游戏！", "游戏未开启", 0)
            # self._from.close()
            return False
        else:
            return True

    # 连通性检测
    def check_connectivity(self):
        match_code = get_system_info()
        if match_code:
            try:
                codelogin, reslogin = QtRequest(f"/check_login/{match_code}", "GET")
                if reslogin.get("code") < 0:
                    # 用户已登录
                    QMessageBox.warning(self, "错误", reslogin.get("message"))
                    self._from.close()
                    return
                code, res = QtRequest(f"/check_expiry/{match_code}", "GET")
                if res.get("code") >= 0:
                    if res.get("message") == "用户已到期":
                        # 关闭当前窗口 展示 reject_From 窗口
                        self.reject_From = reject_From()
                        self.reject_From.show()
                        self._from.close()
                    else:
                        return True
                else:
                    self.reject_From = reject_From()
                    self.reject_From.show()
                    self._from.close()
            except Exception as e:
                print("请求出现错误", e)
                QMessageBox.warning(self, "错误", "网络连接失败,请检查你的DNS")
                self._from.close()
                return False
        else:
            QMessageBox.warning(self, "错误", "无法获取机器码")
            self._from.close()
            return False
        pass

    # 检查redis是否开启 且 可以连接
    def redisState(self):
        try:
            process = QProcess()
            # 尝试获取Redis进程列表
            process.start('tasklist /fi "imagename eq redis-server.exe"')
            process.waitForFinished()  # 等待命令执行完成
            # 获取命令执行的输出
            output = process.readAll()
            # 使用系统默认编码尝试解码输出
            try:
                output_str = output.data().decode("cp1252")  # 尝试使用cp1252编码
            except UnicodeDecodeError as e:
                print("错误1", e)
                QMessageBox.warning(self, "错误", "redis检查失败，请检查是否安装redis")
                self._from.close()
                return False
            # 检查输出中是否包含redis-server.exe
            if "redis-server.exe" in output_str:
                return True
            else:
                QMessageBox.warning(self, "错误", "redis检查失败，请检查是否安装redis")
                return False
        except Exception as e:
            print("错误", e)
            QMessageBox.warning(self, "错误", "redis检查失败，请检查是否安装redis")
            self._from.close()
            return False

    # 检查图片资源是否存在
    def loading_images(self):
        # try:
        # 获取资源列表
        httpurl = "xxxxx"
        files_list = QtRequest("/get_files", "GET")
        if int(files_list[0]) != 200:
            QMessageBox.warning(self, "错误", "获取资源列表失败")
            return False
        if int(files_list[1].get("code")) < 0:
            QMessageBox.warning(self, "错误", "获取资源列表失败")
            return False
        _list = files_list[1].get("data")
        global_images_path = os.path.join(os.path.expanduser("~"), "ChickenBrothers")
        no_load_files = []
        # 循环判断 _list 中的文件是否存在
        for file in _list:
            save_path = os.path.normpath(os.path.join(global_images_path, file))
            if not os.path.exists(save_path):
                # 将 public\death\2.png 格式的路径格式化为 url
                url = f"{httpurl}/{os.path.basename(file)}".replace("\\", "/")
                print(url)
                no_load_files.append({"url": url, "save_path": save_path})
                # 记录不存在文件的名称
        if len(no_load_files) > 0:
            self.updatelabels.valueChanged.emit("正在下载资源...")
            # 下载图片资源
            for i, file in enumerate(no_load_files):
                _file = requests.get(file["url"]).content
                if not os.path.exists(os.path.dirname(file["save_path"])):
                    os.makedirs(os.path.dirname(file["save_path"]))
                # 将图片保存到指定路径的指定文件
                with open(file["save_path"], "wb") as f:
                    f.write(_file)
                # 更新进度条
                self.signal_emitter.valueChanged.emit(
                    int((i + 1) / len(no_load_files) * 100)
                )
        return True

    # 检查是否包含ocr
    def check_ocr(self):
        global_images_path = os.path.join(os.path.expanduser("~"), "ChickenBrothers")
        ocr_file = os.path.join(global_images_path, "ocr", "tesseract.exe")
        httpurl = "xxxxx"
        # 判断是否有这个文件
        if not os.path.exists(ocr_file):
            # 下载 httpurl 文件
            # 下载文件
            try:
                # 下载文件
                _file = requests.get(httpurl).content
                # 将图片保存到指定路径的指定文件
                with open(global_images_path, "wb") as f:
                    f.write(_file)
                # windows解压文件
                subprocess.Popen(
                    f"tar -xf {global_images_path} -C {global_images_path}",
                    shell=True,
                )
                return True
            except Exception as e:
                print("错误", e)
                QMessageBox.warning(self, "错误", "资源下载失败")
                return False

    # 检查是否包含ocr
    def check_ocr_new(self):
        global_images_path = os.path.join(
            os.path.expanduser("~"), "ChickenBrothers", "ocr.zip"
        )
        ocr_file = os.path.join(
            os.path.expanduser("~"), "ChickenBrothers", "ocr", "tesseract.exe"
        )
        ocr_directory = os.path.join(os.path.expanduser("~"), "ChickenBrothers", "ocr")
        httpurl = "xxxxx"

        # 判断是否有这个文件
        if not os.path.exists(ocr_file):
            try:
                self.updatelabels.valueChanged.emit("正在下载资源...")
                # 下载文件并显示进度条
                response = requests.get(httpurl, stream=True)
                total_length = int(response.headers.get("content-length", 0))

                with open(global_images_path, "wb") as f:
                    dl = 0
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            f.write(chunk)
                            dl += len(chunk)
                            done = int(100 * dl / total_length)
                            # 更新进度条
                            self.signal_emitter.valueChanged.emit(done)
                # 使用 zipfile 解压文件到指定目录
                with zipfile.ZipFile(global_images_path, 'r') as zip_ref:
                    zip_ref.extractall(ocr_directory)
                return True
            except Exception as e:
                print("错误", e)
                QMessageBox.warning(self, "错误", "资源下载失败")
                return False
        else:
            return True

    # except Exception as e:
    # print("错误", e)
    # QMessageBox.warning(self, "错误", "资源下载失败")
    # return False
