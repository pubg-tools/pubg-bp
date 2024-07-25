from typing import Union
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Query
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import datetime, uuid, uvicorn
from db.mymongo import MongoDBWrapper, encrypt_with_private_key_pem
from copy import deepcopy
from fastapi.middleware.cors import CORSMiddleware
import asyncio, json
from fastapi import Body
from db.myredis import RedisWrapper
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import timedelta

pubgDB = MongoDBWrapper("localhost", 27017, "pubg")
pubgUserDB = MongoDBWrapper("localhost", 27017, "pubgUserLogger")
myRedis = RedisWrapper("localhost", 6379, 2)

# 连接redis

hashkey = "xxxxxx"
key = "xxxxxx"

app = FastAPI(debug=True)

# 允许所有来源的跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
def read_root():
    return {"version": "v2.3.0"}


# 获取文件表
@app.get("/get_files")
def get_files():
    try:
        result = pubgDB.find_documents("files", {"key": "images"})
        files = list(result)
        if files:
            return {"code": 0, "data": files[0]["list"]}
        else:
            return {"code": 0, "data": []}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "error"}


# 错误上报的接收接口
@app.post("/error_report")
def error_report(
    data: str = Body(...), windows_id: str = Body(...), version: str = Body(...)
):
    try:
        # 先判断该机器码是否存在这个错误
        result = pubgDB.find_documents(
            "error_report",
            {"windows_id": windows_id, "version": version, "error": data},
        )
        error = list(result)
        if error:
            return {"code": 0, "message": "已经上报过了"}
        pubgDB.insert_document(
            "error_report",
            {
                "error": data,
                "createTime": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
                "windows_id": windows_id,
                "version": version,
            },
        )
        return {"code": 0, "message": "success"}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "error"}


class CloudAccountReportData(BaseModel):
    # "map_name": "",  # 点位名称
    # "map": "",  # 地图
    # "start_time": "",  # 开始时间
    # "bp": 0,  # bp数量
    # "death_time": "",  # 死亡时间
    # "windows_id": self.windows_id,  # 机器码
    # "version": self.version,  # 版本号
    # "user_id": self.pip_user_id,  # 用户id
    map_name: str
    map_: str
    start_time: str
    bp: int
    death_time: str
    windows_id: str
    version: str
    user_id: str


# 云账号统计数据上报
@app.post("/cloud_account_report")
def cloud_account_report(data: CloudAccountReportData = Body(...)):
    try:
        if data and data.user_id:
            # 判断是否已经有了这条数据 通过 data.start_time
            result = pubgUserDB.find_documents(
                data.user_id,
                {"start_time": data.start_time, "user_id": data.user_id},
            )
            if list(result):
                return {"code": 0, "message": "已经上报过了"}
            pubgUserDB.insert_document(data.user_id, data.dict())
            return {"code": 0, "message": "success"}
        pass
    except Exception as e:
        print(e)
        return {"code": -1, "message": "error"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 检查卡密是否过期
@app.get("/check_card/{card_id}")
def check_card(card_id: str):
    try:
        result = pubgDB.find_documents(
            "cards", {"card": encrypt_with_private_key_pem(card_id, key)}
        )
        card = list(result)
        if card:
            if card[0]["status"] == "未激活":
                return {"code": 0, "message": "未激活", "type": card[0]["type"]}
            else:
                # 查询是那个用户激活的 返回到期时间
                result = pubgDB.find_documents(
                    "users", {"windows_id": card[0]["windows_id"]}
                )
                user = list(result)
                if user:
                    return {
                        "code": 0,
                        "message": "已激活",
                        "endTime": user[0]["endTime"],
                        "windows_id": user[0]["windows_id"],
                    }
                else:
                    return {"code": -1, "message": "卡密不可用"}
        else:
            return {"code": -1, "message": "卡密不存在"}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "error"}


# 更新某张卡密的信息与状态 （web端用）
@app.post("/update_card/{card_id}")
def web_update_card(card_id: str, email: str, windows_id: str):
    try:
        # 获取卡密信息
        result = pubgDB.find_documents(
            "cards", {"card": encrypt_with_private_key_pem(card_id, key)}
        )
        if windows_id is None:
            return {"code": -1, "message": "windows_id 不能为空"}
        else:
            # 获取用户信息
            result = pubgDB.find_documents("users", {"windows_id": windows_id})
            user = list(result)
            # 判断用户是否存在 且 未到期
            if user.endTimeKey < int(datetime.datetime.now().timestamp()):
                return {"code": -1, "message": "用户不存在或已到期"}
            # 计算还有多少天到期
            one_day = 24 * 60 * 60
            end_time = user[0]["endTimeKey"]
            current_time = int(datetime.datetime.now().timestamp())
            day = (end_time - current_time) / one_day

        pass
    except Exception as e:
        pass
    pass


# 创建卡密
@app.post("/create_card")
def create_card(type: str, nums: int, apikey: str):
    global key, pubgDB
    keys = []
    try:
        if key == apikey:
            for i in range(nums):
                _uuid = str(uuid.uuid4()).replace("-", "")
                card = {
                    "card": str(encrypt_with_private_key_pem(str(_uuid), key)),
                    "type": str(type),
                    "status": "未激活",
                    "createTime": str(
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    ),
                }
                card_copy = deepcopy(card)
                card["card"] = _uuid
                pubgDB.insert_document("cards", card_copy)
                keys.append(card)
            return {"code": 0, "hashed_str": keys}
        else:
            return {"code": 0, "message": "Invalid key"}
    except Exception as e:
        print(e)
        return {"code": 0, "message": "Invalid key"}


# 激活卡密
@app.put("/activate_card/{card_id}")
def activate_card(card_id: str, windows_id: str):
    try:
        # 查询卡密是否存在以及状态
        km_result = pubgDB.find_documents(
            "cards", {"card": encrypt_with_private_key_pem(card_id, key)}
        )
        card = list(km_result)
        # 判断卡密是否激活
        if card:
            if card[0]["status"] != "未激活":
                return {"code": 0, "message": "卡密已被使用"}
        else:
            return {"code": -1, "message": "卡密不存在"}
        result = pubgDB.find_documents("users", {"windows_id": windows_id})
        user = list(result)
        # 卡密可使用时间
        card_end_time = int(card[0]["type"])
        current_time = int(datetime.datetime.now().timestamp())
        one_day = 24 * 60 * 60
        if user:
            # 判断用户是否到期 到期返回 已经到期
            if user[0]["endTimeKey"] < current_time:
                query = {"card": encrypt_with_private_key_pem(card_id, key)}
                update = {"$set": {"status": "已激活", "windows_id": windows_id}}
                pubgDB.update_document("cards", query, update)
                # 更新用户信息
                user[0]["cards"].append(card_id)
                user[0]["endTimeKey"] = current_time + (one_day * card_end_time)
                user[0]["endTime"] = datetime.datetime.fromtimestamp(
                    user[0]["endTimeKey"]
                ).strftime("%Y-%m-%d %H:%M")
                query = {"windows_id": windows_id}
                update = {"$set": user[0]}
                pubgDB.update_document("users", query, update)
                return {"code": 0, "message": "重新激活成功"}
            else:
                # 续期
                user[0]["cards"].append(card_id)
                user[0]["endTimeKey"] = int(user[0]["endTimeKey"]) + (
                    one_day * card_end_time
                )
                user[0]["endTime"] = datetime.datetime.fromtimestamp(
                    user[0]["endTimeKey"]
                ).strftime("%Y-%m-%d %H:%M")
                # 修改用户信息
                query = {"windows_id": windows_id}
                update = {"$set": user[0]}
                pubgDB.update_document("users", query, update)
                # 修改卡密状态
                query = {"card": encrypt_with_private_key_pem(card_id, key)}
                update = {"$set": {"status": "已激活", "windows_id": windows_id}}
                pubgDB.update_document("cards", query, update)
                return {"code": 0, "message": "续期成功"}
        else:
            end_time = current_time + (one_day * card_end_time)
            user_obj = {
                "windows_id": windows_id,
                "cards": [card_id],
                "createTime": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
                "endTimeKey": end_time,
                "endTime": datetime.datetime.fromtimestamp(end_time).strftime(
                    "%Y-%m-%d %H:%M"
                ),
            }
            user_cp = deepcopy(user_obj)
            # 创建新用户
            pubgDB.insert_document("users", user_cp)
            query = {"card": encrypt_with_private_key_pem(card_id, key)}
            update = {"$set": {"status": "已激活", "windows_id": windows_id}}
            pubgDB.update_document("cards", query, update)
            return {"code": 0, "message": "激活成功", "user": user_obj}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "error"}


# 删除卡密
@app.delete("/delete_card/{card_id}")
def delete_card(card_id: str):
    try:
        # 查询卡密是否存在
        km_result = pubgDB.find_documents(
            "cards", {"card": encrypt_with_private_key_pem(card_id, key)}
        )
        card = list(km_result)
        # 判断卡密是否存在
        if card:
            # 删除卡密
            pubgDB.delete_document(
                "cards", {"card": encrypt_with_private_key_pem(card_id, key)}
            )
            return {"code": 0, "message": "卡密删除成功"}
        else:
            return {"code": -1, "message": "卡密不存在"}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "error"}


# 删除某个用户
@app.delete("/delete_user/{windows_id}")
def delete_user(windows_id: str):
    try:
        result = pubgDB.find_documents("users", {"windows_id": windows_id})
        user = list(result)
        if user:
            pubgDB.delete_document("users", {"windows_id": windows_id})
            return {"code": 0, "message": "用户删除成功"}
        else:
            return {"code": -1, "message": "用户不存在"}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "error"}


# 检查到期
@app.get("/check_expiry/{windows_id}")
def check_expiry(windows_id: str):
    try:
        result = pubgDB.find_documents("users", {"windows_id": windows_id})
        user = list(result)
        if user:
            current_time = int(datetime.datetime.now().timestamp())
            if user[0]["endTimeKey"] < current_time:
                return {"code": 0, "message": "用户已到期"}
            else:
                return {
                    "code": 0,
                    "message": "用户未到期",
                    "endTime": user[0]["endTime"],
                }
        else:
            return {"code": -1, "message": "用户不存在"}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "出现未知错误"}


# 检查是否登录
@app.get("/check_login/{windows_id}")
def check_login(windows_id: str):
    try:
        # 判断 redis 中是否有这个用户
        if myRedis.get(windows_id):
            return {"code": -1, "message": "该账号已在其他地方登录！"}
        else:
            return {"code": 0, "message": "该账号未登录"}
    except Exception as e:
        print(e)
        return {"code": -1, "message": "出现未知错误"}


# 换绑
@app.put("/change_bind/{card_id}")
def change_bind(card_id: str):
    try:
        # 查询那个用户绑定了这个卡密
        result = pubgDB.find_documents(
            "cards", {"card": encrypt_with_private_key_pem(card_id, key)}
        )
        card = list(result)
        if card:
            if card[0]["status"] == "已激活":
                # 查询该用户
                result = pubgDB.find_documents(
                    "users", {"windows_id": card[0]["windows_id"]}
                )
                user = list(result)
                # 判断是否已到期 / 到期时间小于三天
                current_time = int(datetime.datetime.now().timestamp())
                if user[0]["endTimeKey"] < current_time:
                    return {"code": 0, "message": "用户已到期"}
                elif user[0]["endTimeKey"] - current_time < 3 * 24 * 60 * 60:
                    return {"code": 0, "message": "到期时间小于三天,无法换绑"}
                else:
                    # 计算到期时间还有多少天
                    one_day = 24 * 60 * 60
                    end_time = user[0]["endTimeKey"]
                    current_time = int(datetime.datetime.now().timestamp())
                    day = (end_time - current_time - one_day) / one_day
                    # 修改卡密状态
                    query = {"card": encrypt_with_private_key_pem(card_id, key)}
                    update = {"$set": {"status": "未激活", "type": int(day)}}
                    pubgDB.update_document("cards", query, update)
                    # 删除旧用户
                    pubgDB.delete_document(
                        "users", {"windows_id": card[0]["windows_id"]}
                    )
                    return {"code": 0, "message": "换绑成功"}
            else:
                return {"code": 0, "message": "未激活的卡密无法换绑"}
        else:
            return {"code": -1, "message": "卡密不存在"}
        pass
    except Exception as e:
        pass


# 长连接 动态检查到期
@app.websocket("/check_expiry_long/{windows_id}")
async def websocket_endpoint(websocket: WebSocket, windows_id: str):
    try:
        # 验证令牌
        await websocket.accept()
        if not await validate_token(windows_id):
            raise ValueError("无效的机器码/该机器已过期")
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5)
                if data:
                    print("接收到的数据", data)
                    _result = json.loads(data)
                    if _result["version"] is None or _result["version"] not in [
                        "v2.3.0",
                        "v2.8.1",
                    ]:
                        print("版本不一致")
                        await websocket.send_text("版本不一致")
                        break
                else:
                    print("接收到的数据为空")
                    break
            except asyncio.TimeoutError:
                print("接收数据超时")
            except Exception as e:
                print("接收数据异常", e)
            # 处理接收到的数据
            print(windows_id + "已连接")
            # 判断是否有这个用户  并且该用户未到期
            result = pubgDB.find_documents("users", {"windows_id": windows_id})
            user = list(result)
            print("用户信息", user)
            if user:
                current_time = int(datetime.datetime.now().timestamp())
                if user[0]["endTimeKey"] > current_time:
                    # 向 redis 中写入 windows_id  过期时间为 3分钟
                    myRedis.set(windows_id, windows_id, 180)
                    await websocket.send_text("未到期")
                else:
                    await websocket.send_text("已到期")
                    websocket.close()
            else:
                await websocket.send_text("已到期")
                websocket.close()
                print("用户不存在")
            await asyncio.sleep(5)

    except ValueError as e:
        # 处理令牌验证失败的情况
        await websocket.send_text(f"错误: {str(e)}")
    except WebSocketDisconnect:
        # 处理客户端断开连接的情况
        print(f"{windows_id}--客户端断开了连接")
    except Exception as e:
        # 处理其他异常
        print(f"发生未预期的异常")
    finally:
        # 无论发生什么，都会执行的代码
        print(f"{windows_id}----WebSocket 连接已关闭")
        # 删除 redis 中的 windows_id
        myRedis.delete(windows_id)
        try:
            await websocket.close(code=3000)  # 使用自定义的关闭代码
        except Exception as e:
            print("关闭连时已经关闭了")


# 验证令牌是否过期
async def validate_token(windows_id: str):
    # 判断是否有这个用户  并且该用户未到期
    result = pubgDB.find_documents("users", {"windows_id": windows_id})
    user = list(result)
    if user:
        current_time = int(datetime.datetime.now().timestamp())
        print("时间戳", current_time, user[0]["endTimeKey"], current_time)
        if user[0]["endTimeKey"] > current_time:
            return True
    return False


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=18081)
