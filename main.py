from src.templates.init import init_Form
from PyQt5 import QtWidgets
import sys
import cv2
import matplotlib
import pyautogui
import multiprocessing
import pytesseract
from src.API.base import base_url
import zipfile
import pyautogui
import pytesseract
import os


os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'.\Lib\site-packages\PyQt5\Qt5\plugins\platforms'



# import ssl
# import _ssl


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = init_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())