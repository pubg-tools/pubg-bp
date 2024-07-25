# from src.myClass.globadata import Singleton
# from src.myClass.myopencv import ImageFinder
# from src.model.myopencv import ImageFinder
# from src.model.globadata import Singleton
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os
import subprocess
import time
import requests
import src.mycv.myopencv as myopencv
import subprocess
import platform
import psutil
import base64, hashlib
from src.API.base import base_url
import cv2, pyautogui
import numpy as np

public_key_str = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuUCLTaMdFjI7nt7JaopY
W/P2zA3A0O7oj/2tT0snm9SDGXZ+qti6sLZ7q03Gp4SndvccXEwb6oubYimGtaym
JCiezWlc7pEaGxzuji0bJmZ1a2SG/FlhioOL1y7O+5dAjCtxhrjG9E9U9AvVTNOS
+rUHNr4peHQkb4AzaKs6LaKpvRjw6QKIWT8DmjuAbsi4TJIH49nHwLv3AorB0nQY
ea5rkAlXysDIfU82LRrCwqbFoD6lNF9/sOAUyQ5IA/Kx/IcIe1cypTBImdJVBKXz
Nsx8GnWbadnMoBUKWVUfa2jUIXLaRq7QI3s+tfMH6rD5x4iqlNL5JCx/K6eVWGVW
PwIDAQAB
-----END PUBLIC KEY-----"""

finder = myopencv.ImageFinder(imgopcv=0.8)
global_images_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"src","public")


# 获取给定文件夹下的所有图片的绝对路径
def find__img_list(autoPath: str) -> list:
    """
    获取给定文件夹下的所有图片的绝对路径。

    Args:
        autoPath (str): 文件夹路径。

    Returns:
        list: 包含所有图片绝对路径的列表。

    """
    project_path = global_images_path
    # 获取某个文件夹下的所有图片
    dir_path = os.path.join(project_path, autoPath)
    # 获取文件夹下的所有图片
    imgs = os.listdir(dir_path)
    # 获取图片的绝对路径
    imgs = [os.path.join(dir_path, img) for img in imgs]
    return imgs


# 获取某个文件
def find_project_file(autoPath: str) -> str:
    """
    获取某个文件的绝对路径。
    Args:
        autoPath (str): 文件路径。
    Returns:
        str: 文件的绝对路径。
    """
    project_path = global_images_path
    # 获取文件的绝对路径
    file_path = os.path.join(project_path, autoPath)
    return file_path


# 在给定的autoPath中查找图片列表，并在窗口中找到这些图片的中心点
def find_imgs(autoPath: str) -> tuple:
    """
    在给定的autoPath中查找图片列表，并在窗口中找到这些图片的中心点。

    Args:
        autoPath (str): 图片路径。

    Returns:
        tuple: 包含图片中心点的元组。

    """
    imgs = find__img_list(autoPath)
    # 获取窗口大小
    center_point = finder.find_images_all(imgs)
    return center_point


# 在给定的autoPath中查找图片列表，并在窗口中找到这些图片的中心点
def find_img_target(autoPath: str) -> tuple:
    """
    在给定的autoPath中查找一张图片，并在窗口中找到这个图片的中心点。

    Args:
        autoPath (str): 图片路径。
        target: 目标。

    Returns:
        tuple: 包含图片中心点的元组。

    """
    imgs = find_project_file(autoPath)
    center_point = finder.find_image_all(imgs)
    return center_point


# 二极化匹配
def find_imgs_binary(autoPath: str, target, imgopcv=0.5) -> tuple:
    target_path = find_project_file(autoPath)
    return finder.find_one_img_screen_pubg(
        target_path,
        target,
        imgopcv=imgopcv,
        isgray=True,
    )


# 相对于某个坐标系找到单张图
def find_img_target_relative(autoPath: str, target, imgopcv=0.5) -> tuple:
    imgs = find_project_file(autoPath)
    return finder.find_one_img_screen_pubg(
        imgs,
        target,
        imgopcv=imgopcv,
        cv_type="TM_CCORR_NORMED",
    )


# 判断顶部罗盘中心的颜色
def find_color(x, y) -> list:
    """find_color(x, y) -> list

    Args:
        x (int): x坐标。
        y (int): y坐标。

    Returns:
        list: 返回颜色的列表。
    """
    target = finder.find_color(int(x), int(y))
    return target.tolist()


# 判断给定的颜色是否在指定的区间范围内
def is_in_intervals(color, intervals) -> bool:
    """
    判断给定的颜色是否在指定的区间范围内。
    Args:
        color (list): 表示颜色的列表，包含RGB三个通道的值。
        intervals (list): 包含颜色区间的列表，每个区间由最小值和最大值组成。

    Returns:
        bool: 如果颜色在所有通道的区间范围内，则返回True；否则返回False。
    """
    for i, value in enumerate(color):
        if not (intervals[i][0] <= value <= intervals[i][1]):
            return False
    return True


# 坐标系计算函数
def determine_quadrant_and_distance_with_tolerance(x, y, tolerance=3):
    # 坐标系的中心点坐标
    center_x = 259 / 2
    center_y = 259 / 2

    # 计算与中心点的距离差
    distance_x = x - center_x
    distance_y = y - center_y

    # 判断点是否在中心点附近
    if abs(distance_x) <= tolerance and abs(distance_y) <= tolerance:
        quadrant = "中心点附近"
    elif distance_x == 0:  # 点在y轴上
        quadrant = "y轴"
    elif distance_y == 0:  # 点在x轴上
        quadrant = "x轴"
    else:
        # 判断点所在的象限
        if x > center_x and y > center_y:
            quadrant = "第一象限"
        elif x < center_x and y > center_y:
            quadrant = "第二象限"
        elif x < center_x and y < center_y:
            quadrant = "第三象限"
        elif x > center_x and y < center_y:
            quadrant = "第四象限"

    # 返回象限和距离差
    return quadrant, distance_x, distance_y


def get_machine_code():
    # 获取机器码
    try:
        # 使用wmic命令获取硬件信息
        result = (
            subprocess.check_output("wmic csproduct get uuid", shell=True)
            .decode()
            .split("\n")[1]
            .strip()
        )
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None


# 创建一个自定义的弹窗
def createPop(imgPath, title="获取CDK"):
    """
    创建一个自定义的弹窗，展示从网络获取的图片。
    参数：
    - imgPath:str,图片的URL路径
    - title:str,弹窗的标题,默认为"获取CDK"
    返回值：
    无返回值
    """
    # 从网络获取图片
    response = requests.get(imgPath)
    # 获取图片内容
    content = response.content
    # 将图片内容转换为QByteArray
    image_data = bytearray(content)
    # 创建QPixmap并从QByteArray加载图片
    pixmap = QPixmap()
    pixmap.loadFromData(image_data, "JPG")  # 指定图片格式
    # 创建一个自定义的弹窗
    dialog = QDialog()
    dialog.setWindowTitle(title)
    # 不显示问号
    dialog.setWindowFlags(Qt.WindowCloseButtonHint)
    # 创建一个QLabel用于展示图片
    label = QLabel()
    # 设置图片到QLabel
    # 创建一个模态对话框
    dialog.setModal(True)
    label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))  # 根据需要调整大小
    # 创建一个垂直布局
    layout = QVBoxLayout()
    # 将QLabel添加到布局中
    layout.addWidget(label)
    # 设置弹窗的布局
    dialog.setLayout(layout)
    # 显示弹窗
    dialog.show()
    dialog.exec_()


def get_system_info():
    # 初始化系统信息字典
    info = {"cpu_model": platform.processor()}

    # 获取BIOS版本
    if platform.system() == "Windows":
        try:
            info["bios_version"] = (
                subprocess.check_output("wmic bios get smbiosbiosversion", shell=True)
                .decode()
                .split("\n")[1]
                .strip()
            )
        except Exception as e:
            info["bios_version"] = str(e)
    elif platform.system() == "Darwin":
        try:
            info["bios_version"] = (
                subprocess.check_output(
                    "system_profiler SPHardwareDataType | grep 'Boot ROM Version'",
                    shell=True,
                )
                .decode()
                .split(": ")[1]
                .strip()
            )
        except Exception as e:
            info["bios_version"] = str(e)

    # 获取主板型号
    if platform.system() == "Windows":
        try:
            info["motherboard_model"] = (
                subprocess.check_output("wmic baseboard get product", shell=True)
                .decode()
                .split("\n")[1]
                .strip()
            )
        except Exception as e:
            info["motherboard_model"] = str(e)
    elif platform.system() == "Darwin":
        try:
            info["motherboard_model"] = (
                subprocess.check_output(
                    "system_profiler SPHardwareDataType | grep 'Model Identifier'",
                    shell=True,
                )
                .decode()
                .split(": ")[1]
                .strip()
            )
        except Exception as e:
            info["motherboard_model"] = str(e)

    # # 获取磁盘序列号
    # if platform.system() == "Windows":
    #     try:
    #         info["disk_serial"] = (
    #             subprocess.check_output("wmic diskdrive get serialnumber", shell=True)
    #             .decode()
    #             .split("\n")[1]
    #             .strip()
    #         )
    #     except Exception as e:
    #         info["disk_serial"] = str(e)
    # elif platform.system() == "Darwin":
    #     try:
    #         info["disk_serial"] = (
    #             subprocess.check_output(
    #                 "system_profiler SPSerialATADataType | grep 'Serial Number'",
    #                 shell=True,
    #             )
    #             .decode()
    #             .split(": ")[1]
    #             .strip()
    #         )
    #     except Exception as e:
    #         info["disk_serial"] = str(e)

    # 获取显卡型号
    if platform.system() == "Windows":
        try:
            info["gpu_model"] = (
                subprocess.check_output(
                    "wmic path win32_videocontroller get name", shell=True
                )
                .decode()
                .split("\n")[1]
                .strip()
            )
        except Exception as e:
            info["gpu_model"] = str(e)
    elif platform.system() == "Darwin":
        try:
            info["gpu_model"] = (
                subprocess.check_output(
                    "system_profiler SPDisplaysDataType | grep 'Chipset Model'",
                    shell=True,
                )
                .decode()
                .split(": ")[1]
                .strip()
            )
        except Exception as e:
            info["gpu_model"] = str(e)

    info["old_code"] = get_machine_code()
    # 获取内存大小、CPU核心数
    info["memory_size"] = str(round(psutil.virtual_memory().total / (1024**3))) + " GB"
    info["processor_count"] = str(psutil.cpu_count(logical=False))
    hash_object = hashlib.sha256()
    hash_object.update(str(info).encode("utf-8"))
    return hash_object.hexdigest()




# 相对于点来找色
def find_colors(x, y, length=30):
    try:
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        points_and_colors = [(x + i, y, img_rgb[y, x + i]) for i in range(length)]
        return points_and_colors
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# 寻找指定点位 2
def findColorTarget2(x=1920 / 2, y=35, length=30):
    intervals = [(10, 66), (169, 237), (172, 251)]  # 目标点颜色区间
    points_and_colors = find_colors(int(x), int(y), length)
    if points_and_colors:
        for px, py, color in points_and_colors:
            if is_in_intervals(color, intervals):
                print("符合条件的点位置：", (px, py))
                return (px, py)
        print("没有符合条件的点")
        return None
    else:
        print("没有找到任何点")
        return None


if __name__ == "__main__":
    # result = find__img_list("public\\error")
    result = get_system_info()
    print(result)
