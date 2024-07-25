from time import sleep
from src.tools.tools import (
    find_imgs,
    find_img_target,
    find_color,
    find_imgs_binary,
    determine_quadrant_and_distance_with_tolerance,
    find__img_list,
    find_img_target_relative,
    findColorTarget2,
)
from src.model.myredis import RedisWrapper
import multiprocessing
import json, random, win32con, win32api, time, math, pydirectinput
from src.API.base import QtRequest
import cv2
import numpy as np
from PIL import ImageGrab, Image
import os
from datetime import datetime
import pytesseract

pydirectinput.FAILSAFE = False
global_images_path = os.path.join(os.path.expanduser("~"), "ChickenBrothers")

pytesseract.pytesseract.tesseract_cmd = os.path.join(
    global_images_path, "ocr", "tesseract.exe"
)


class PUBGClass:
    def __init__(
        self,
        maps,
        windows_id,
        pip_user_id=None,
        randomMap=False,
        planeTime=30,
        bpImageSavePath=None,
        ImageSavaPath=None,
    ) -> None:
        self.version = "v2.8.1"
        self.maps = maps  # 地图数据
        self.randomMap = randomMap  # 随机标点
        self.planeTime = planeTime  # 跳伞延迟时间
        self.loopStart = multiprocessing.Value("b", False)
        self.loopTow = multiprocessing.Value("b", False)
        self.windows_id = windows_id
        self.bpImageSavePath = bpImageSavePath
        self.ImageSavaPath = ImageSavaPath
        self.pip_user_id = pip_user_id

        # 同步统计信息
        game_manger = multiprocessing.Manager()
        self.game_dict = game_manger.dict(
            {
                "map_name": "",  # 点位名称
                "map_": "",  # 地图
                "start_time": "",  # 开始时间
                "bp": 0,  # bp数量
                "death_time": "",  # 死亡时间
                "windows_id": self.windows_id,  # 机器码
                "version": self.version,  # 版本号
                "user_id": self.pip_user_id,  # 用户id
            }
        )
        pass

    # 开始游戏 和 结束游戏 的进程
    def playHomeLoop(self):
        """
        用于检查是否在主页，如果在主页则开始游戏。
        如果为在主页则检查其他错误情况/弹窗。
        """
        self.loopStart.value = True
        errorMaps = find__img_list("public\\error")
        myredis = RedisWrapper()
        myredis.flushall()
        myredis.set("classState", "开始挂机")
        # 开启一个主循环
        while self.loopStart.value:
            try:
                # 是否在主页
                if self.isMainPage():
                    while self.loopStart.value:
                        for item in errorMaps:
                            # 426,154,1429,797,宽高(1003,643)
                            positions = find_imgs_binary(
                                item, (426, 154, 1429, 797), 0.7
                            )
                            print("检查弹窗", positions)
                            if positions[0] is not None:
                                myredis.set("classState", "有弹窗需要点击")
                                pydirectinput.moveTo(
                                    positions[0] + 426, positions[1] + 154
                                )
                                sleep(1)
                                pydirectinput.click()
                                sleep(1)
                        break
                    # 清空 redis 的所有值
                    myredis.flushall()
                    self.startGame()  # 开始游戏
                    # 设置为已点击开始游戏 按钮
                else:
                    # 是否死亡
                    self.characherDeath()  # 检查死亡
                # 循环的延迟
                sleep(1)
            except Exception as e:
                print("错误", e)
                self.updateErrors(e)
                myredis.set("classState", f"出现异常-如果影响游戏正常流程，请反馈")
                sleep(1)

    # 开始游戏后，游戏中的主进程
    def gameMainLoop(self):
        # print("gameMainLoop")
        myredis = RedisWrapper()
        myredis.set("classState", "开始挂机-2")
        while self.loopStart.value:
            print("挂机中")
            # myredis.set("classState", "挂机中")
            try:
                if self.loopTow.value:
                    self.waitGame()  # 检查是否在等待状态
                    self.inPlane()  # 检查是否在飞机上 在的话 等待跳伞
                sleep(1)
            except Exception as e:
                self.updateErrors(e)
                myredis.set("classState", f"出现异常-如果影响游戏正常流程，请反馈")
                sleep(1)

    def updateErrors(self, error):
        version = self.version
        err = str(error)
        print(res)

    def stop(self):
        myredis = RedisWrapper()
        myredis.flushall()
        self.loopStart.value = False
        self.loopTow.value = False

    # 判断我们是否在主页
    def isMainPage(self):
        positions = find_imgs("public\\home")
        if positions[0] is not None:
            return True
        else:
            return False

    # 开始游戏
    def startGame(self):
        positions = find_imgs("public\\startGame")
        if positions[0] is not None:
            pydirectinput.moveTo(positions[0], positions[1])
            sleep(1)
            pydirectinput.click()
            self.loopTow.value = True
            return

    # 落地死亡后
    def characherDeath(self):
        myredis = RedisWrapper()
        # 检查是否死亡
        while self.loopStart.value:
            positions = find_imgs("public\\death")
            if positions[0] is None:
                break
            else:
                if self.bpImageSavePath:
                    # 判断是否有 bp 那张图
                    positions_bp = find_img_target_relative(
                        "public\\bp\\bp.jpg", (92, 281, 237, 342), 0.8
                    )
                    if positions_bp[0] is not None:
                        self.capture_screen_region(
                            92, 281, 145, 61, self.bpImageSavePath, "BP图片"
                        )

                # 上报数据
                if self.pip_user_id:
                    # 判断是否有 bp 那张图
                    positions_bp = find_img_target_relative(
                        "public\\bp\\bp.jpg", (92, 281, 237, 342), 0.8
                    )
                    if positions_bp[0] is not None:
                        # 记录bp数量
                        self.game_dict["bp"] = self.get_bp_nums(92, 281, 145, 61)
                        # 记录死亡时间
                        self.game_dict["death_time"] = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        # _, res = QtRequest(
                        #     "/cloud_account_report", "POST", data=dict(self.game_dict)
                        # )
                        # # print("上报数据", self.pip_user_id, dict(self.game_dict))
                        # if res and res.get("code") == -1:
                        #     myredis.set("classState", "上报数据异常")
                        #     time.sleep(2)
                        # else:
                        #     myredis.set("classState", "提交数据成功")
                        #     time.sleep(1)

                # print("死亡")
                myredis.set("classState", "死亡")
                myredis.set("kill", "1")
                self.loopTow.value = False
                pydirectinput.moveTo(positions[0], positions[1])
                sleep(1)
                pydirectinput.click()
                pass
            sleep(1)

    # 广场等待
    def waitGame(self):
        myredis = RedisWrapper()
        # 读取是否开始游戏
        start = myredis.get("wait")
        while self.loopTow.value and start is None:
            positions = find_imgs("public\\wait")
            if positions[0] is not None:
                try:
                    myredis.set("classState", "在出生岛等待")
                    # 更新 记录数据 开始时间
                    self.game_dict["start_time"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    # 开地图 判断是那张地图
                    pydirectinput.moveTo(300, 300)
                    sleep(1)
                    pydirectinput.click()
                    sleep(1)
                    pydirectinput.press("m")
                    map_name = self.checkMap()  # 当前地图名称
                    if map_name is not None:
                        myredis.set("classState", f"获取到的地图名称 {map_name}")
                        map_data = self.maps[map_name]  # 当前地图数据
                        # 根据 map_data 的数组长度 随机取值
                        map_number = random.randint(0, len(map_data) - 1)
                        # 本局点位
                        # 判断是否是随机抽取点位
                        if self.randomMap and len(map_data) > 1:
                            # 随机抽取点位
                            myredis.set("dies", json.dumps(map_data[map_number]))
                        else:
                            map_number = 0
                            # 将点位存入 dies
                            myredis.set("dies", json.dumps(map_data[0]))
                        # 开始标记第一个点
                        _map_data = map_data[map_number]
                        self.game_dict["map_name"] = _map_data.get("name")
                        pydirectinput.moveTo(
                            _map_data.get("dian1").get("x"),
                            _map_data.get("dian1").get("y"),
                        )
                        sleep(1)
                        # 右键标记目标点
                        pydirectinput.rightClick()
                        # 缩放滚轮打开详细位置
                        self.mouse_scroll_up(30)
                        sleep(1)
                        # 关闭地图
                        pydirectinput.press("m")
                        sleep(1)
                        # 切换第一人称
                        pydirectinput.press("v")
                        # 向 redis 存入 当前已经开始游戏
                        myredis.set("wait", "1")
                        myredis.set("classState", "标点结束-现在应该是第一人称")
                        break
                    else:
                        pydirectinput.press("m")
                        self.game_end_funtion()
                        myredis.set("wait", "1")
                        myredis.set("classState", "没找到地图数据-啥也不干")
                        break
                except Exception as e:
                    print("错误", e)
                    myredis.set("wait", "1")
                    myredis.set("classState", "没找到地图数据-啥也不干")
                    break
            else:
                print("不处于等待")
                myredis.set("classState", "不处于等待")
                break

    # 是否在飞机上
    def inPlane(self):
        # 判断是否在飞机上
        positions = find_imgs("public\\inPlane")
        if positions[0] is not None:
            start_time = time.time()  # 开始时间
            while self.loopTow.value:
                if time.time() - start_time > self.planeTime:
                    # 到时间了 要跳伞
                    start_time = time.time()
                    myredis = RedisWrapper()
                    while self.loopTow.value:
                        kill = myredis.get("kill")
                        if kill is not None:
                            return
                        if time.time() - start_time > 60:
                            myredis.set("classState", "寻找目标点超时")
                            return
                        result = findColorTarget2(x=960, y=35, length=140)
                        if result:
                            break
                        else:
                            win32api.mouse_event(
                                win32con.MOUSEEVENTF_MOVE, int(15) * 20, 0
                            )
                    pydirectinput.press("f")
                    self.jump()  # 跳伞后 寻找目标点 找到目标点后 开启降落伞
                    break
                else:
                    sleep(1)

    # 开始跳伞
    def jump(self):
        myredis = RedisWrapper()
        luodi = myredis.get("luodi")
        if luodi is not None:
            return
        # 寻找目标点
        # self.findTarget(20)
        start_time = time.time()
        # start_time_key = 14
        while self.loopTow.value:
            kill = myredis.get("kill")
            if kill is not None:
                return
            if time.time() - start_time > 60:
                myredis.set("classState", "寻找目标点超时")
                return
            result = findColorTarget2(x=960, y=35, length=1)
            if result:
                break
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 20, 0)
                time.sleep(0.2)
        # 找到目标点后 延迟5秒 按f
        for i in range(14):
            if self.loopTow.value == False:
                return
            pydirectinput.press("f")
            # print("跳伞")
            myredis.set("classState", "跳伞")
            sleep(1)
        # 按下 ctrl + w 向目标点飞行
        pydirectinput.keyDown("ctrl")
        pydirectinput.keyDown("w")
        while self.loopTow.value:
            if findColorTarget2(881, 35, 160) is None:
                pydirectinput.keyUp("ctrl")
                break

        # 判断右下角是否有目标点
        # count = 0
        # _find_target_start_time = time.time()
        # while self.loopTow.value:
        #     if time.time() - _find_target_start_time > 600:
        #         print("寻找目标点超时")
        #         myredis.set("classState", "寻找目标点超时-这局放弃")
        #         myredis.set("luodi", "1")
        #         self.loopTow.value = False
        #         return
        #     tx, ty = find_imgs_binary(
        #         "public\\target\\dianpng.png",
        #         (1628, 792, 1890, 1052),
        #     )
        #     if tx and ty:
        #         count += 1
        #         if count > 5:
        #             # 确定小地图有目标点
        #             pydirectinput.keyUp("ctrl")
        #             quadrant, _, _ = determine_quadrant_and_distance_with_tolerance(
        #                 tx, ty + 10, 50
        #             )
        #             if quadrant == "中心点附近":
        #                 break
        #     else:
        #         # 判断是否落地
        #         positions = find_imgs_binary(
        #             "public\\landing\\1920_luodi_game2.png", (688, 966, 750, 1037), 0.7
        #         )
        #         if positions[0] is not None:
        #             print("提前落地")
        #             myredis.set("classState", "并未到达目标点提前落地-这局放弃")
        #             # 并未到达目标点提前落地
        #             pydirectinput.keyUp("a")
        #             pydirectinput.keyUp("w")
        #             pydirectinput.keyUp("ctrl")
        #             myredis.set("luodi", "1")
        #             return
        #     sleep(1)
        # 开始落地
        # print("开始落地")
        myredis.set("classState", "开始落地")
        pydirectinput.keyUp("ctrl")
        pydirectinput.keyDown("a")
        _find_luodi_start_time = time.time()
        while self.loopTow.value:
            if time.time() - _find_luodi_start_time > 600:
                myredis.set("classState", "寻找落地点超时-这局放弃")
                myredis.set("luodi", "1")
                self.game_end_funtion()
                self.loopTow.value = False
                return
            # 判断是否落地
            positions = find_imgs_binary(
                "public\\landing\\1920_luodi_game2.png",
                (688, 966, 750, 1037),
                0.7,
            )
            if positions[0] is not None:
                pydirectinput.keyUp("a")
                pydirectinput.keyUp("w")
                break
            sleep(1)
        # 兜底双按键
        pydirectinput.keyUp("a")
        pydirectinput.keyUp("w")
        # 落地了
        myredis.set("luodi", "1")
        follow = myredis.get("follow")
        if follow is not None:
            myredis.set("classState", "没有读取到地图数据-这局放弃")
            return
        # 判断小地图是否有目标点
        # positions = find_imgs_binary(
        #     "public\\target\\dianpng.png",
        #     (1628, 792, 1890, 1052),
        # )
        # redis_dist = myredis.get("dies")
        # if redis_dist is None:
        #     return
        # 准备地图数据
        redis_dist = myredis.get("dies")
        if redis_dist is None:
            myredis.set("classState", "没有拿到地图数据-这局放弃")
            return
        dies = json.loads(redis_dist)
        dian2_x, dian2_y = dies.get("dian2").get("x"), dies.get("dian2").get("y")
        dian3_x, dian3_y = dies.get("dian3").get("x"), dies.get("dian3").get("y")
        # 取出后续逻辑
        follow_up = dies.get("times")

        self.runToTarget()
        sleep(1)
        # 标记第二个目标点
        self.markTarget(dian2_x, dian2_y)
        # # 判断小地图是否有标点
        # positions = find_imgs_binary(
        #     "public\\target\\dianpng.png",
        #     (1628, 792, 1890, 1052),
        # )
        # if positions[0] is not None:
        #     myredis.set("classState", "没有到达目标点附近-这局放弃")
        #     return
        sleep(1)
        self.runToTarget()
        sleep(1)
        # 标记第三个目标点
        self.markTarget(dian3_x, dian3_y)
        sleep(1)
        self.runToTarget()
        # print("到达目标点")
        myredis.set("classState", "到达目标点")
        # 执行后续逻辑
        self.followUp(follow_up)
        # print("执行完毕")
        myredis.set("classState", "执行完毕")
        self.game_end_funtion()
        return

    # 判断是那张地图
    def checkMap(self) -> str | None:
        map_path = "public\\maps\\"
        # 判断是否有维寒迪
        position = find_img_target(map_path + "whd.png")
        if position[0] is not None:
            self.game_dict["map_"] = "维寒迪"
            return "whd"
        # 判断是否有泰格
        position = find_img_target(map_path + "tg.png")
        if position[0] is not None:
            self.game_dict["map_"] = "泰格"
            return "tg"
        # 判断是否有容都
        position = find_img_target(map_path + "rd.png")
        if position[0] is not None:
            self.game_dict["map_"] = "容都"
            return "rd"
        # 判断是否有米拉码
        position = find_img_target(map_path + "mlm.png")
        if position[0] is not None:
            self.game_dict["map_"] = "米拉码"
            return "mlm"
        # 判断是否有艾伦格
        position = find_img_target(map_path + "alg.png")
        if position[0] is not None:
            self.game_dict["map_"] = "艾伦格"
            return "alg"
        # 判断是否有萨诺
        position = find_img_target(map_path + "sn.png")
        if position[0] is not None:
            self.game_dict["map_"] = "萨诺"
            return "sn"
        # 判断是否有卡拉金
        position = find_img_target(map_path + "klj.png")
        if position[0] is not None:
            self.game_dict["map_"] = "卡拉金"
            return "klj"
        # 判断是否有帝斯顿
        position = find_img_target(map_path + "dsd.png")
        if position[0] is not None:
            self.game_dict["map_"] = "帝斯顿"
            return "dsd"
        return None

    # 缩放滚轮
    def mouse_scroll_up(self, lines):
        """
        模拟鼠标向上滚动指定的行数。

        :param lines: 要滚动的行数
        """
        WHEEL_DELTA = 120
        for _ in range(lines):
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, WHEEL_DELTA, 0)
            sleep(0.01)

    # 寻找目标点
    def findTarget(self, speed=20):
        # start_time = time.time()
        # intervals = [(10, 66), (169, 237), (172, 251)]  # 目标点颜色区间
        # myredis = RedisWrapper()
        # while self.loopTow.value:
        #     kill = myredis.get("kill")
        #     if kill is not None:
        #         return
        #     if time.time() - start_time > 60:
        #         myredis.set("classState", "寻找目标点超时")
        #         return
        #     color_list = find_color(1920 / 2, 35)
        #     # 判断颜色是否在我们目标点区间
        #     if self.is_in_intervals(color_list, intervals):
        #         break
        #     else:
        #         win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, speed, 0)
        start_time = time.time()
        myredis = RedisWrapper()
        while self.loopTow.value:
            kill = myredis.get("kill")
            if kill is not None:
                return
            if time.time() - start_time > 60:
                myredis.set("classState", "寻找目标点超时")
                return
            result = findColorTarget2(x=960, y=35, length=140)
            if result:
                break
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(15) * 20, 0)
                # time.sleep(1)
        start_time = time.time()
        while self.loopTow.value:
            kill = myredis.get("kill")
            if kill is not None:
                return
            if time.time() - start_time > 60:
                myredis.set("classState", "寻找目标点超时")
                return
            result = findColorTarget2(x=960, y=35, length=1)
            if result:
                break
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, speed, 0)
                time.sleep(0.2)

    # 跑向目标点
    def runToTarget(self):
        myredis = RedisWrapper()
        # 寻找目标点
        self.findTarget(20)
        start_time = time.time()
        pydirectinput.press("=")
        # 开始奔跑后，判断是否到达目标点 626,15,1297,115,宽高(671,100) 881,19,1041,119,宽高(160,100)
        while self.loopTow.value:
            time.sleep(1)
            if time.time() - start_time > 60:
                myredis.set("classState", "跑向目标点超时")
                return
            pydirectinput.press("f")
            # 938, 35, 43
            if findColorTarget2(938, 35, 43) is None:
                pydirectinput.press("=")
                break
        # 向后修正
        start_time = time.time()
        while self.loopTow.value:
            if findColorTarget2(881, 35, 160):
                break
            else:
                pydirectinput.keyDown("s")
                time.sleep(0.5)
                pydirectinput.keyUp("s")
        # pydirectinput.keyDown("w")
        # time.sleep(1)
        # pydirectinput.keyUp("w")

    # 判断颜色是否在目标点区间
    def is_in_intervals(self, color, intervals):
        for i, value in enumerate(color):
            if not (intervals[i][0] <= value <= intervals[i][1]):
                return False
        return True

    # 标记目标点
    def markTarget(self, x, y):
        pydirectinput.moveTo(x, y)
        sleep(1)
        pydirectinput.press("m")
        sleep(1)
        pydirectinput.moveTo(x, y)
        sleep(1)
        pydirectinput.rightClick()
        sleep(1)
        pydirectinput.press("m")

    # 执行到达目标点后的逻辑
    def followUp(self, follow_up):
        # print("执行到达目标点后的逻辑", follow_up)
        myredis = RedisWrapper()
        follow = myredis.get("follow")
        if follow is not None:
            return
        key_list = [
            "a",
            "w",
            "s",
            "d",
            "c",
            "z",
            "tab",
            "space",
            "1",
            "2",
            "3",
            "f",
            "=",
        ]
        for item in follow_up:
            match_key = item.get("key")
            # print(match_key)
            match item.get("key"):
                case "a" | "A":
                    key, type_key, time = (
                        item.get("key"),
                        item.get("type"),
                        item.get("time"),
                    )
                    if type_key == "click":
                        sleep(0.3)
                        pydirectinput.press("a")
                        sleep(0.3)
                    else:
                        sleep(0.3)
                        pydirectinput.keyDown("a")
                        sleep(int(time))
                        pydirectinput.keyUp("a")
                        sleep(0.3)
                case "w" | "W":
                    key, type_key, time = (
                        item.get("key"),
                        item.get("type"),
                        item.get("time"),
                    )
                    if type_key == "click":
                        sleep(0.3)
                        pydirectinput.press("w")
                        sleep(0.3)
                    else:
                        sleep(0.3)
                        pydirectinput.keyDown("w")
                        sleep(int(time))
                        pydirectinput.keyUp("w")
                        sleep(0.3)
                case "s" | "S":
                    key, type_key, time = (
                        item.get("key"),
                        item.get("type"),
                        item.get("time"),
                    )
                    if type_key == "click":
                        sleep(0.3)
                        pydirectinput.press("s")
                        sleep(0.3)
                    else:
                        sleep(0.3)
                        pydirectinput.keyDown("s")
                        sleep(int(time))
                        pydirectinput.keyUp("s")
                        sleep(0.3)
                case "d" | "D":
                    key, type_key, time = (
                        item.get("key"),
                        item.get("type"),
                        item.get("time"),
                    )
                    if type_key == "click":
                        sleep(0.3)
                        pydirectinput.press("d")
                        sleep(0.3)
                    else:
                        sleep(0.3)
                        pydirectinput.keyDown("d")
                        sleep(int(time))
                        pydirectinput.keyUp("d")
                        sleep(0.3)
                case "c" | "C":
                    key, type_key, time = (
                        item.get("key"),
                        item.get("type"),
                        item.get("time"),
                    )
                    if type_key == "click":
                        sleep(0.3)
                        pydirectinput.press("c")
                        sleep(0.3)
                    else:
                        sleep(0.3)
                        pydirectinput.keyDown("c")
                        sleep(int(time))
                        pydirectinput.keyUp("c")
                        sleep(0.3)
                case "z" | "Z":
                    key, type_key, time = (
                        item.get("key"),
                        item.get("type"),
                        item.get("time"),
                    )
                    if type_key == "click":
                        sleep(0.3)
                        pydirectinput.press("z")
                        sleep(0.3)
                    else:
                        sleep(0.3)
                        pydirectinput.keyDown("z")
                        # print("按下z time", time)
                        sleep(int(time))
                        pydirectinput.keyUp("z")
                        sleep(0.3)
                case "tab" | "Tab":
                    sleep(0.3)
                    pydirectinput.press("tab")
                    sleep(0.3)
                case "space" | "Space":
                    sleep(0.3)
                    pydirectinput.press("space")
                    sleep(0.3)
                case "1":
                    sleep(0.3)
                    pydirectinput.press("1")
                    sleep(0.3)
                case "2":
                    sleep(0.3)
                    pydirectinput.press("2")
                    sleep(0.3)
                case "3":
                    sleep(0.3)
                    pydirectinput.press("3")
                    sleep(0.3)
                case "f":
                    sleep(0.3)
                    pydirectinput.press("f")
                    sleep(0.3)
                case "=":
                    sleep(0.3)
                    pydirectinput.press("=")
                    sleep(0.3)
                case match_key if match_key in key_list:
                    if type_key == "Down":
                        pydirectinput.keyDown(key)
                        sleep(int(time))
                        pydirectinput.keyUp(key)
                    else:
                        pydirectinput.press(key)
                case "jdx":
                    key, nums, time = (
                        item.get("key"),
                        item.get("time"),
                        item.get("time"),
                    )
                    for i in range(int(nums)):
                        pydirectinput.moveTo(154, 122)
                        pydirectinput.rightClick()
                        sleep(1)
                case "leftClick":
                    pydirectinput.click()
                case "rightClick":
                    pydirectinput.rightClick()
                case "leftDown":
                    time = item.get("time")
                    pydirectinput.mouseDown(button="left")
                    sleep(int(time))
                    pydirectinput.mouseUp(button="left")
                case "rightDown":
                    time = item.get("time")
                    pydirectinput.mouseDown(button="right")
                    sleep(int(time))
                    pydirectinput.mouseUp(button="right")
                case "wait":
                    time = item.get("time")
                    sleep(int(time))
                case "ctrl+1":
                    pydirectinput.keyDown("ctrl")
                    sleep(1)
                    pydirectinput.press("1")
                    pydirectinput.keyUp("ctrl")
                case None:
                    return
                case _:
                    pass
            sleep(1)
        myredis.set("follow", "1")

    # 截取屏幕指定区域 并保存
    def capture_screen_region(
        self, x, y, width, height, save_directory, ImagesPathName
    ):
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
        current_time_mkdir = datetime.now().strftime("%Y-%m-%d")  # 使用 - 代替 : 符号
        # 生成保存路径和文件名
        output_filename = f"{current_time}.jpg"
        output_path = os.path.join(
            save_directory, ImagesPathName, current_time_mkdir, output_filename
        )
        # 确保保存目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # 保存图像
        try:
            # 使用Pillow保存图像
            screen_pil.save(output_path)
            print(f"图像成功保存到 {output_path}")
        except Exception as e:
            print(f"保存图像时出现错误: {e}")

    # 获取bp数量
    def get_bp_nums(self, x, y, width, height):
        try:
            # 截取屏幕指定区域
            bbox = (x, y, x + width, y + height)
            screen = ImageGrab.grab(bbox=bbox)
            screen_np = np.array(screen)
            # 将图像从RGB转换为BGR（OpenCV使用BGR格式）
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)
            # 使用Pytesseract进行OCR
            custom_config = r"--oem 3 --psm 6 outputbase digits"
            text = pytesseract.image_to_string(screen_bgr, config=custom_config)
            return str(text).strip()
        except Exception as e:
            print(f"获取BP数量时出现错误: {e}")
            return -1

    # 统一结束后执行钩子
    def game_end_funtion(self):
        # 调用截图
        if self.ImageSavaPath:
            self.capture_screen_region(
                0, 0, 1920, 1080, self.ImageSavaPath, "目标点图片"
            )
        else:
            print("没有设置图片保存路径", self.ImageSavaPath)
        print("游戏结束")
        pass
