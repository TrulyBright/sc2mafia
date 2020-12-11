import aiosqlite
from passlib.hash import sha256_crypt

import re


class ImproperUsernameError(Exception):
    """
    Raised when username is improper
    """

class ImproperNicknameError(Exception):
    """
    Raised when nickname is improper
    """

class NicknameDuplicateError(Exception):
    """
    Raised when nickname is already occupied
    """

class UsernameDucpliateError(Exception):
    """
    Raised when username is already occupied
    """

def proper_username(username):
    return username.isalnum()


def proper_nickname(nickname):
    # 한글과 영어와 숫자로만 되었는지 판별하는 함수
    return len(re.findall('[가-힣]|[a-z]|[A-Z]|[0-9]', username)) == len(username)


async def authenticate(username, password) -> bool:
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
            raise ImproperUsernameError
        query = f"SELECT * FROM users WHERE username='{username}'"
        cursor = await DB.execute(query)
        user = await cursor.fetchone()
        if user is not None:  # username already occupied
            raise UsernameDucpliateError

        if not proper_nickname(nickname):
            raise ImproperNicknameError

        query = f"SELECT * FROM users WHERE nickname='{nickname}'"
        cursor = await DB.execute(query)
        user = await cursor.fetchone()
        if user is not None:  # nickname already occupied
            raise NicknameDuplicateError

        query = f"INSERT INTO users(username, password, nickname) VALUES ('{username}', '{sha256_crypt.hash(password)}', '{nickname}')"
        await DB.execute(query)
        await DB.commit()
        return True


async def get_nickname(username) -> str:
    async with aiosqlite.connect('sql/users.db') as DB:
        if not proper_username(username):
            raise ImproperUsernameError
        query = f"SELECT nickname FROM users WHERE username='{username}'"
        cursor = await DB.execute(query)
        nickname = (await cursor.fetchone())[0]
        return nickname
