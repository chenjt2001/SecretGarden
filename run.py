import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Body, Cookie
from fastapi.responses import JSONResponse
import asyncio
from fastapi.responses import HTMLResponse, FileResponse
import hashlib
import os
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import base64
import pymysql


app = FastAPI()

################################################################################
PASSWORD = "917310"

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "chenjintao"
MYSQL_DATABASE = "secretgarden"
MYSQL_CHARSET="utf8mb4"

#!!!!!!!!!!!!!!!!!!!!!!注意
#此处的SALT随机生成，在每个进程中不同！因此不能使用多进程服务
SALT = get_random_bytes(32)

################################################################################


class Messages():
    def __init__(self) -> None:
        pass

    def getDb(self):
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset=MYSQL_CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )

    def add(self, item: dict):
        conn = self.getDb()
        cursor = conn.cursor()
        sql = r"INSERT INTO messages(time, author, text) VALUES(%s, %s, %s)"
        cursor.execute(sql, [item["time"], item["author"], item["content"]])
        conn.commit()
        conn.close()

    def get(self) -> list:
        conn = self.getDb()
        cursor = conn.cursor()
        sql = r"SELECT id, time, author, text AS content from messages"
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
        if len(data) > 0:
            data.sort(key=lambda x:x["id"], reverse=True)
            return data
        return [] # 无数据时，data为tuple

messages = Messages()

################################################################################


def pad(s): return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
def unpad(s): return s[:-ord(s[len(s) - 1:])]


def encryptToken(lastTime: float) -> str:
    """获取token"""
    private_key = hashlib.scrypt(
        b"chenjintao", salt=SALT, n=2**14, r=8, p=1, dklen=32)
    plain_text = pad(str(lastTime))
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_GCM, iv)
    return base64.b64encode(iv + cipher.encrypt(plain_text.encode())).decode()


def decryptToken(token: float) -> float:
    """从token中解密出lastTime"""
    try:
        private_key = hashlib.scrypt(
            b"chenjintao", salt=SALT, n=2**14, r=8, p=1, dklen=32)
        cipher_text = base64.b64decode(token.encode())
        iv = cipher_text[:16]
        cipher = AES.new(private_key, AES.MODE_GCM, iv)
        return float(unpad(cipher.decrypt(cipher_text[16:]).decode()))
    except Exception as e:
        return 0
################################################################################


@app.get("/")
async def index():
    with open('static/index.html', 'r', encoding="utf-8") as f:
        return HTMLResponse(f.read(), 200)


@app.get("/assets/{path:path}", response_class=FileResponse)
async def assets(path: str):
    path = os.path.join('static/assets', path.replace("..", ""))
    if (not os.path.exists(path)) or os.path.isdir(path):
        raise HTTPException(status_code=404)
    return path


@app.post("/api/token")
async def login(
    password: str = Body(..., embed=True)
):
    """登录"""
    if password == PASSWORD:
        token = encryptToken(time.time())
        content = {"status": "success"}
        response = JSONResponse(content=content)
        response.set_cookie(key="access_token", value=token)
        # print(token)
        return response

    # 防止暴力提交
    await asyncio.sleep(0.5)

    raise HTTPException(status_code=403)


def assert_access_token(access_token: str) -> None:
    """判断token是否有效"""
    t = decryptToken(access_token)
    if t == 0:
        raise HTTPException(status_code=403)
    elif time.time() - t > 60*60*24:
        raise HTTPException(status_code=401)


@app.get("/api/messages")
async def get_messages(
    access_token: Optional[str] = Cookie(None)
):
    # print(access_token)
    assert_access_token(access_token)

    return {
        "status": "success",
        "items": messages.get()
    }


@app.post("/api/messages")
async def post_messages(
    access_token: Optional[str] = Cookie(None),
    author: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
):
    # 添加留言
    assert_access_token(access_token)

    item = {"author": author, "content": content, "time": int(time.time())}
    messages.add(item)

    return {"status": "success"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
