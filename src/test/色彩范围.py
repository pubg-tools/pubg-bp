import cv2
import numpy as np
from PIL import ImageGrab
import os


global_images_path = os.path.join(os.path.expanduser("~"), "ChickenBrothers")


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


my_path = find_project_file("public\\target\\dianpng.png")


def capture_screen(region):
    # 截取指定区域的屏幕图像
    screenshot = ImageGrab.grab(bbox=region)
    screenshot_np = np.array(screenshot)
    # 转换颜色空间 PIL (RGB) -> OpenCV (BGR)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    return screenshot_bgr

def find_target_in_region(region, target_image_path, lower_bound_hsv, upper_bound_hsv):
    # 截取屏幕图像
    screen_image = capture_screen(region)
    
    # 将屏幕图像转换为 HSV 颜色空间
    hsv_screen_image = cv2.cvtColor(screen_image, cv2.COLOR_BGR2HSV)
    
    # 创建颜色范围掩膜
    mask = cv2.inRange(hsv_screen_image, lower_bound_hsv, upper_bound_hsv)
    
    # 形态学操作去除噪声（可选）
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 读取目标图像并分离 RGBA 通道
    target_image = cv2.imread(target_image_path, cv2.IMREAD_UNCHANGED)
    
    if target_image is None:
        raise ValueError("目标图像无法读取，请检查路径和文件完整性。")
    
    b, g, r, a = cv2.split(target_image)
    
    # 使用 Alpha 通道确定目标区域
    target_mask = a > 0
    target_pixels = target_image[target_mask]
    target_hsv = cv2.cvtColor(target_pixels[:, :3].reshape(-1, 1, 3), cv2.COLOR_BGR2HSV).reshape(-1, 3)
    
    # 计算目标区域的 HSV 范围（可选：使用实际图像的颜色范围）
    # h_min, s_min, v_min = np.min(target_hsv, axis=0)
    # h_max, s_max, v_max = np.max(target_hsv, axis=0)
    # lower_bound = np.array([h_min, s_min, v_min])
    # upper_bound = np.array([h_max, s_max, v_max])

    # 形态学操作后的结果
    processed_image = cv2.bitwise_and(screen_image, screen_image, mask=mask)

    # 寻找最匹配的轮廓
    target_location = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        roi = hsv_screen_image[y:y+h, x:x+w]
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            continue
        roi_resized = cv2.resize(roi, (target_image.shape[1], target_image.shape[0]))
        mask_target = cv2.inRange(roi_resized, lower_bound_hsv, upper_bound_hsv)
        match_percentage = np.sum(mask_target == 255) / (mask_target.shape[0] * mask_target.shape[1])
        if match_percentage > 0.9:  # 调整阈值以适应具体需求
            target_location = (x, y, x+w, y+h)
            break
    
    return target_location

# 示例调用
region = (0, 0, 1920, 1080)
target_image_path = 'path_to_your_target_image.png'
lower_bound_hsv = np.array([28, 4, 103])
upper_bound_hsv = np.array([150, 222, 255])

target_location = find_target_in_region(region, target_image_path, lower_bound_hsv, upper_bound_hsv)
if target_location:
    print(f"找到目标位置：{target_location}")
else:
    print("未找到目标位置")
