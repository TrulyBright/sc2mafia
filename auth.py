import aiosqlite
from passlib.hash import sha256_crypt

import re


def proper_username(username):
    return username.isalnum()


def proper_nickname(nickname):
    # 한글과 영어와 숫자로만 되었는지 판별하는 함수
    return len(re.findall('[가-힣]|[a-z]|[A-Z]|[0-9]', username)) == len(username)


async def check_credentials(username, password) -> bool:
    async with aiosqlite.connect('sql/users.db') as DB:
        if not proper_username(username):
            return False
        query = f"SELECT * FROM users WHERE username='{username}'"
        cursor = await DB.execute(query)
        user = await cursor.fetchone()
        if user is not None:
            hashed = user[2]
            return sha256_crypt.verify(password, hashed)
    return False


async def create_user(username, password, nickname) -> str:
    async with aiosqlite.connect('sql/users.db') as DB:
        if not proper_username(username):
            return 'improper username'
        query = f"SELECT * FROM users WHERE username='{username}'"
        cursor = await DB.execute(query)
        user = await cursor.fetchone()
        if user is not None:  # username already occupied
            return 'username_duplicate'

        if not proper_nickname(nickname):
            return 'improper nickname'
        query = f"SELECT * FROM users WHERE nickname='{nickname}'"
        cursor = await DB.execute(query)
        user = await cursor.fetchone()
        if user is not None:  # nickname already occupied
            return 'nickname_duplicate'

        query = f"INSERT INTO users(username, password, nickname) VALUES ('{username}', '{sha256_crypt.hash(password)}', '{nickname}')"
        await DB.execute(query)
        await DB.commit()
        return 'success'


async def get_nickname(username) -> str:
    async with aiosqlite.connect('sql/users.db') as DB:
        assert proper_username(username)
        query = f"SELECT nickname FROM users WHERE username='{username}'"
        cursor = await DB.execute(query)
        nickname = (await cursor.fetchone())[0]
        return nickname
