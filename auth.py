import aiosqlite
import sqlalchemy as sa
from passlib.hash import sha256_crypt

import db



async def check_credentials(username, password) -> bool:
  async with aiosqlite.connect('sql/users.db') as DB:
    # where = sa.and_(db.users.c.username==username,
    #             sa.not_(db.users.c.disabled))
    # query = db.users.select().where(where)
    query = f"SELECT * FROM users WHERE username='{username}'"
    cursor = await DB.execute(query)
    user = await cursor.fetchone()
    if user is not None:
      hashed = user[2]
      return sha256_crypt.verify(password, hashed)
  return False


async def create_user(username, password, nickname) -> str:
  async with aiosqlite.connect('sql/users.db') as DB:
    # where = sa.and_(db.users.c.username==username,
    #                 sa.not_(db.users.c.disabled))
    # query = db.users.select().where(where)
    query = f"SELECT * FROM users WHERE username='{username}'"
    cursor = await DB.execute(query)
    user = await cursor.fetchone()
    if user is not None: # username already occupied
      return 'username_duplicate'

    query = f"SELECT * FROM users WHERE nickname='{nickname}'"
    cursor = await DB.execute(query)
    user = await cursor.fetchone()
    if user is not None: # nickname already occupied
      return 'nickname_duplicate'

    query = f"INSERT INTO users(username, password, nickname) VALUES ('{username}', '{sha256_crypt.hash(password)}', '{nickname}')"
    await DB.execute(query)
    await DB.commit()
    return 'success'

async def get_nickname(username) -> str:
  async with aiosqlite.connect('sql/users.db') as DB:
    query = f"SELECT nickname FROM users WHERE username='{username}'"
    cursor = await DB.execute(query)
    nickname = (await cursor.fetchone())[0]
    return nickname
