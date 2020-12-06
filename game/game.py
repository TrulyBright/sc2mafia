import random
import asyncio

from . import roles

class GameRoom:
  def __init__(self, roomID, title, capacity, host, private=False, password=None):
    assert type(title) is str
    assert type(capacity) is int
    assert type(private) is bool
    assert type(password) is str or password is None
    self.roomID = roomID
    self.title = title
    self.capacity = capacity
    self.members = []
    self.host = host
    self.password = password
    self.private = private
    self.inGame = False
    self.justCreated = True

  def isFull(self):
    return len(self.members)>=self.capacity

  async def handle_message(self, sio, sid, msg):
    async with sio.session(sid) as user:
      if msg.startswith('/'):
        if msg=='/시작' and sid==self.host and not self.inGame:
          await self.init_game(sio)
          await self.run_game(sio)
      else:
        to_send = {'who': user['nickname'],
                   'message': msg,}
        await sio.emit('message', to_send, room=self.roomID)


  async def is_game_over(self):
    alive = [p for p in self.players if p.alive]
    for p in alive:
      if p.role.team != alive[0].role.team:
        return False
    return True

  async def init_game(self, sio):
    # init game
    self.inGame = True
    roles_to_distribute = [roles.Mafioso(), roles.Citizen(), roles.Sheriff()]
    random.shuffle(roles_to_distribute)
    self.players = [Player(sid=sid,
                           nickname=(await sio.get_session(sid))['nickname'],
                           role=roles_to_distribute[index])
                           for index, sid in enumerate(self.members)]
    for p in self.players:
      await sio.emit('role', p.role.name, room=p.sid)

  async def run_game(self, sio):
    while True:
      if await self.is_game_over():
        to_send = {
          'winner': [p.nickname for p in self.players if p.alive]
        }
        await sio.emit('game_over', to_send,  room=self.roomID)
        return



class Player:
  def __init__(self, sid, nickname, role):
    self.sid = sid
    self.nickname = nickname
    self.role = role
    self.alive = True
