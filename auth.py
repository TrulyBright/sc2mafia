import aiosqlite
import sqlalchemy as sa
from passlib.hash import sha256_crypt

import db



async def check_credentials(username, password):
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


async def create_user(username, password, nickname):
  async with aiosqlite.connect('sql/users.db') as DB:
    # where = sa.and_(db.users.c.username==username,
    #                 sa.not_(db.users.c.disabled))
    # query = db.users.select().where(where)
    query = f"SELECT * FROM users WHERE username='{username}'"
    cursor = await DB.execute(query)
    user = await cursor.fetchone()
    if user is not None: # username already occupied
      return False
    # query = db.users.insert().values({
    #   'username': username,
    #   'password': sha256_crypt.hash(password),
    #   'nickname': nickname,
    # })
    query = f"INSERT INTO users(username, password, nickname) VALUES ('{username}', '{sha256_crypt.hash(password)}', '{nickname}')"
    await DB.execute(query)
    await DB.commit()
    return True
