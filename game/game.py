from random import randint

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
    self.host = host
    self.members = []
    self.private = private
    self.password = password
    self.inGame = False

  def isFull(self):
    return len(self.members)>=self.capacity

  async def handle_message(self, sio, sid, msg):
    async with sio.session(sid) as user:
      if not self.inGame:
        to_send = {'who': user['username'],
                   'message': msg,}
        await sio.emit('message', to_send, room=self.roomID)
        return

      if msg.startswith('/'):
        if msg=='/시작' and sid==self.host:
          self.start_game(sio)

  async def start_game(self, sio):
    pass



class Player:
  def __init__(self, nickname, role):
    self.nickname = nickname
    self.role = role
    self.alive = True
