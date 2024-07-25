import cv2
import numpy as np
from PIL import ImageGrab, Image
import os
from datetime import datetime


def capture_screen_region(x, y, width, height, save_directory):
    # 截取屏幕指定区域
    bbox = (x, y, x + width, y + height)
    screen = ImageGrab.grab(bbox=bbox)
    screen_np = np.array(screen)

    # 将图像从RGB转换为BGR（OpenCV使用BGR格式）
    screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

    # 将图像从BGR转换为RGB
    screen_rgb = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2RGB)

    # 创建Pillow图像对象
    screen_pil = Image.fromarray(screen_rgb)

    # 获取当前时间并格式化为字符串
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")  # 使用 - 代替 : 符号

    # 生成保存路径和文件名
    output_filename = f"{current_time}.jpg"
    output_path = os.path.join(save_directory,"bp数据","掉毛", output_filename)
    print(output_path)

    # 确保保存目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存图像
    try:
        # 使用Pillow保存图像
        screen_pil.save(output_path)
        print(f"图像成功保存到 {output_path}")
    except Exception as e:
        print(f"保存图像时出现错误: {e}")


if __name__ == "__main__":
    # 示例调用函数，假设find_img_target_relative已经定义并返回合适的坐标
    result = (43, 28)  # 示例坐标
    # 截取置顶区域的图片 保存到指定目录
    current_time = datetime.now().strftime("%Y-%m-%d")  # 使用 - 代替 : 符号
    # print(current_time)
    # print(os.path.join(
    #     "bp截图",
    #     current_time,
    #     current_time,
    # ))

