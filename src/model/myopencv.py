import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import pyautogui


class ImageFinder:
    def __init__(self, imgopcv, search_area_percentages=(0, 0, 1920, 1080)):
        self.imgopcv = imgopcv
        self.search_area_percentages = search_area_percentages
        self.screen_width, self.screen_height = pyautogui.size()

    # 相对于某个坐标系的屏幕截取
    def find_image_in_screen(self, image_path):
        try:
            # 计算截取区域的坐标
            left = int(self.search_area_percentages[0])
            top = int(self.search_area_percentages[1])
            right = int(self.search_area_percentages[2])
            bottom = int(self.search_area_percentages[3])

            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            template = cv2.imdecode(
                np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
            )
            if template is None:
                print(
                    f"Error loading image '{image_path}'. Check the file path and integrity."
                )
                return None
            w, h = template.shape[::-1]

            # 将屏幕图像转换为灰度图
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

            # 模板匹配
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

            # 设定匹配阈值
            threshold = self.imgopcv
            loc = np.where(res >= threshold)

            # 寻找最佳匹配位置
            if len(loc[0]) > 0:
                # 找到最大值的索引
                pt = np.unravel_index(
                    res.argmax(), res.shape
                )  # 使用 argmax 找到最大值的索引

                # 计算匹配区域的中心点坐标
                center_point = (
                    pt[1] + w / 2,
                    pt[0] + h / 2,
                )  # pt[1] 是列索引，pt[0] 是行索引
                return center_point
            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于整个屏幕的屏幕截取
    def find_image_all(self, image_path):
        try:
            # 截取屏幕图像
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            # 读取目标图片并转换为灰度图
            image_path = f"{image_path}"
            template = cv2.imdecode(
                np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
            )
            if template is None:
                print(
                    f"Error loading image '{image_path}'. Check the file path and integrity."
                )
                return None
            w, h = template.shape[::-1]
            # 将屏幕图像转换为灰度图
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            # 模板匹配
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            # 设定匹配阈值
            threshold = self.imgopcv
            loc = np.where(res >= threshold)
            # 寻找最佳匹配位置
            if len(loc[0]) > 0:
                # 找到最大值的索引
                pt = np.unravel_index(
                    res.argmax(), res.shape
                )  # 使用 argmax 找到最大值的索引

                # 计算匹配区域的中心点坐标
                center_point = (
                    pt[1] + w / 2,
                    pt[0] + h / 2,
                )  # pt[1] 是列索引，pt[0] 是行索引
                return center_point
            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于整个屏幕截取找多张图
    def find_images_all(self, image_paths):
        try:
            # 计算截取区域的坐标
            left = int(self.search_area_percentages[0])
            top = int(self.search_area_percentages[1])
            right = int(self.search_area_percentages[2])
            bottom = int(self.search_area_percentages[3])
            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

            # 循环遍历提供的图片路径列表
            for image_path in image_paths:
                # image_path = plt.imread(image_path)
                # 读取目标图片并转换为灰度图
                image_path = f"{image_path}"
                template = cv2.imdecode(
                    np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
                )
                if template is None:
                    print(
                        f"Error loading image '{image_path}'. Check the file path and integrity."
                    )
                    continue  # 如果图片加载失败，跳过这张图片

                w, h = template.shape[::-1]  # 获取图片的宽度和高度

                # 将屏幕图像转换为灰度图
                img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

                # 模板匹配
                res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

                # 设定匹配阈值
                threshold = self.imgopcv
                loc = np.where(res >= threshold)

                # 寻找最佳匹配位置
                if len(loc[0]) > 0:
                    # 找到最大值的索引
                    pt = np.unravel_index(res.argmax(), res.shape)

                    # 计算匹配区域的中心点坐标
                    center_point = (pt[1] + w // 2, pt[0] + h // 2)
                    return center_point  # 返回第一张找到的图片的中心点坐标

            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于某个坐标系 来找到 单张图
    def find_one_img_screen_pubg(
        self,
        img_pas,
        search_area_percentages,
        imgopcv=0.5,
        cv_type="COLOR_RGB2BGR",
        isgray=False,
    ):
        try:
            cv_type_list = {
                "COLOR_RGB2BGR": cv2.COLOR_RGB2BGR,
                "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
            }
            project_path = os.path.dirname(os.path.dirname(__file__))
            img1_path = np.fromfile(
                os.path.join(project_path, img_pas),
                dtype=np.uint8,
            )
            img1 = cv2.imdecode(img1_path, -1)
            # 获取图片的宽高
            h, w = img1.shape[:2]
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            # 获取屏幕
            left = int(search_area_percentages[0])
            top = int(search_area_percentages[1])
            right = int(search_area_percentages[2])
            bottom = int(search_area_percentages[3])
            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)

            # 将屏幕图像转换为灰度图
            img_rgb = cv2.cvtColor(screen_np, cv_type_list[cv_type])
            gray2 = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            # 判断是否进行二极化
            if isgray:
                # #########方法3，自动指定阈值，小于127是黑色，大于127是白色
                ret, binary1 = cv2.threshold(gray1, 127, 255, cv2.THRESH_BINARY)
                ret, binary2 = cv2.threshold(gray2, 127, 255, cv2.THRESH_BINARY)
                res = cv2.matchTemplate(binary1, binary2, cv2.TM_CCOEFF_NORMED)
                # cv2.imshow("origin", target)
                # print("yuzhi:", ret)  # 自动计算的分割阈值
                # cv2.imshow("binary", binary)
            else:
                res = cv2.matchTemplate(gray2, gray1, cv2.TM_CCOEFF_NORMED)
            # 设定匹配阈值
            threshold = imgopcv
            loc = np.where(res >= threshold)
            # 寻找最佳匹配位置
            if len(loc[0]) > 0:
                # 找到最大值的索引
                pt = np.unravel_index(res.argmax(), res.shape)
                # 计算匹配区域的中心点坐标
                center_point = (pt[1] + w // 2, pt[0] + h // 2)
                return center_point
            else:
                return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于某个坐标系 来找到 单张图 加解密
    def find_one_img_screen_pubg_with_encryption_decryption(
        self,
        encrypted_img_path,
        search_area_percentages,
        decryption_key,
        imgopcv=0.5,
        cv_type="COLOR_RGB2BGR",
        isgray=False,
    ):
        """相对于某个坐标系 来找到 单张图 包含加解密

        Args:
            encrypted_img_path (str): 图像加密后的路径
            search_area_percentages (str): 解密图像的key的路径
            decryption_key (str): 解密图像的key的路径
            imgopcv (float, optional): 图片相似度. Defaults to 0.5.
            cv_type (str, optional): 模板匹配类型. Defaults to "COLOR_RGB2BGR".
            isgray (bool, optional): 是否使用二极化. Defaults to False.

        Returns:
            元组: 包含图片中心点的元组。(None,None) (int,int)
        """
        try:
            cv_type_list = {
                "COLOR_RGB2BGR": cv2.COLOR_RGB2BGR,
                "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
            }
            # 加载加密的图片
            encrypted_img = cv2.imread(encrypted_img_path, cv2.IMREAD_UNCHANGED)
            # 使用提供的解密秘钥对图片进行解密
            decrypted_img = self.decryption(encrypted_img, decryption_key)
            img1 = decrypted_img
            # 获取图片的宽高
            h, w = img1.shape[:2]
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            # 获取屏幕
            left = int(search_area_percentages[0])
            top = int(search_area_percentages[1])
            right = int(search_area_percentages[2])
            bottom = int(search_area_percentages[3])
            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)

            # 将屏幕图像转换为灰度图
            img_rgb = cv2.cvtColor(screen_np, cv_type_list[cv_type])
            gray2 = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            # 判断是否进行二极化
            if isgray:
                # #########方法3，自动指定阈值，小于127是黑色，大于127是白色
                ret, binary1 = cv2.threshold(gray1, 127, 255, cv2.THRESH_BINARY)
                ret, binary2 = cv2.threshold(gray2, 127, 255, cv2.THRESH_BINARY)
                res = cv2.matchTemplate(binary1, binary2, cv2.TM_CCOEFF_NORMED)
            else:
                res = cv2.matchTemplate(gray2, gray1, cv2.TM_CCOEFF_NORMED)
            # 设定匹配阈值
            threshold = imgopcv
            loc = np.where(res >= threshold)
            # 寻找最佳匹配位置
            if len(loc[0]) > 0:
                # 找到最大值的索引
                pt = np.unravel_index(res.argmax(), res.shape)
                # 计算匹配区域的中心点坐标
                center_point = (pt[1] + w // 2, pt[0] + h // 2)
                return center_point
            else:
                return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于整个屏幕截取找多张图 加解密
    def find_image_all_with_encryption_decryption(
        self,
        image_path,
        image_path_key,
    ):
        try:
            # 截取屏幕图像
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)  # 屏幕图像
            # 读取目标图片并转换为灰度图
            # 加载加密的图片
            encrypted_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            # 使用提供的解密秘钥对图片进行解密
            decrypted_img = self.decryption(encrypted_img, image_path_key)
            # 将 decrypted_img 转换为灰度图
            template = cv2.cvtColor(decrypted_img, cv2.COLOR_BGR2GRAY)
            if template is None:
                print(
                    f"Error loading image '{image_path}'. Check the file path and integrity."
                )
                return (None, None)
            w, h = template.shape[::-1]
            # 将屏幕图像转换为灰度图
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            # 模板匹配
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            # 设定匹配阈值
            threshold = self.imgopcv
            loc = np.where(res >= threshold)
            # 寻找最佳匹配位置
            if len(loc[0]) > 0:
                # 找到最大值的索引
                pt = np.unravel_index(
                    res.argmax(), res.shape
                )  # 使用 argmax 找到最大值的索引
                # 计算匹配区域的中心点坐标
                center_point = (
                    pt[1] + w / 2,
                    pt[0] + h / 2,
                )  # pt[1] 是列索引，pt[0] 是行索引
                return center_point
            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于整个屏幕截取多张图 找图片 加解密
    def find_images_all_with_encryption_decryption(self, image_paths, image_path_keys):
        try:
            # 计算截取区域的坐标
            left = int(self.search_area_percentages[0])
            top = int(self.search_area_percentages[1])
            right = int(self.search_area_percentages[2])
            bottom = int(self.search_area_percentages[3])
            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

            # 循环遍历提供的图片路径列表
            for i, image_path in enumerate(image_paths):
                # 读取加密的图片
                encrypted_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                # 使用提供的解密秘钥对图片进行解密
                decrypted_img = self.decryption(encrypted_img, image_path_keys[i])
                # 将 decrypted_img 转换为灰度图
                template = cv2.cvtColor(decrypted_img, cv2.COLOR_BGR2GRAY)
                if template is None:
                    print(
                        f"Error loading image '{image_path}'. Check the file path and integrity."
                    )
                    continue
                w, h = template.shape[::-1]
                # 将屏幕图像转换为灰度图
                img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
                # 模板匹配
                res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                # 设定匹配阈值
                threshold = self.imgopcv
                loc = np.where(res >= threshold)
                # 寻找最佳匹配位置
                if len(loc[0]) > 0:
                    # 找到最大值的索引
                    pt = np.unravel_index(res.argmax(), res.shape)
                    # 计算匹配区域的中心点坐标
                    center_point = (
                        pt[1] + w / 2,
                        pt[0] + h / 2,
                    )
                    return center_point
            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    def decryption(self, img, key):
        """
        将图像进行解密
        :param img: 加密后的图片
        :param key: 秘钥
        :return: 返回一个解密后的图片
        """
        img_decrypted = cv2.bitwise_xor(img, key)
        return img_decrypted

    def find_color(self, x, y):
        try:
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            color = img_rgb[y, x]
            return color
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


# 使用示例
if __name__ == "__main__":
    finder = ImageFinder()
    target_image_path = "../images/kaishi.jpg"
    search_area_percentages = (
        (0.1, 0.1),  # 顶部 left right
        (0.9, 0.1),  # 底部 left right
    )
    result = finder.find_image_in_screen(target_image_path, search_area_percentages)
    if result is not None:
        print(f"Found image at screen coordinates: {result}")
    else:
        print("No match found.")
