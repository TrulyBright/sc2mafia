import aiosqlite
import re




class ImproperNicknameError(Exception):
    """
    Raised when nickname is improper
    """


class NicknameDuplicateError(Exception):
    """
    Raised when nickname is already occupied
    """

class NicknameTooLongError(Exception):
    """
    Raised when nickname has more than 8 characters
    """


def proper_nickname(nickname):
    # 한글과 영어와 숫자로만 되었는지 판별하는 함수
    return nickname!='' and len(re.findall('[가-힣]|[a-z]|[A-Z]|[0-9]', nickname)) == len(nickname)


async def create_user(naverId, nickname):
    async with aiosqlite.connect('sql/users.db') as DB:
        if not proper_nickname(nickname):
            raise ImproperNicknameError
        if re.findall("[가-힇]", nickname):
            if len(nickname)>8:
                raise NicknameTooLongError
        elif len(nickname)>12:
            raise NicknameTooLongError
        query = f"SELECT * FROM users WHERE nickname='{nickname}'"
        cursor = await DB.execute(query)
        user = await cursor.fetchone()
        if user is not None:  # nickname already occupied
            raise NicknameDuplicateError
        query = f"INSERT INTO users(naverId, nickname) VALUES ({naverId}, '{nickname}')"
        await DB.execute(query)
        await DB.commit()


async def getUserByNaverId(naverId):
    async with aiosqlite.connect('sql/users.db') as DB:
        query = f"SELECT * FROM users WHERE naverId={naverId}"
        cursor = await DB.execute(query)
        user = await cursor.fetchone()
        return user
