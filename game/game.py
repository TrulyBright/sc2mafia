import random
import asyncio
from datetime import datetime, timedelta

from . import roles

class GameRoom:
  def __init__(self, roomID, title, capacity, host, setup, private=False, password=None):
    assert type(title) is str
    assert type(capacity) is int
    assert type(private) is bool
    assert type(password) is str or password is None
    self.roomID = roomID
    self.title = title
    self.capacity = capacity
    self.members = []
    self.host = host
    self.setup = setup
    self.password = password
    self.private = private
    self.inGame = False
    self.justCreated = True

  def isFull(self):
    return len(self.members)>=self.capacity

  async def handle_message(self, sio, sid, msg):
    async with sio.session(sid) as user:
      if msg.startswith('/'):
        msg = msg.split()
        if len(msg)==3:
          cmd, target1, target2 = msg
          assert target1 in self.players
          assert target2 in self.players
        elif len(msg)==2:
          cmd, target = msg
          assert target in self.players
        else:
          cmd = msg[0]
        if cmd=='/시작' and sid==self.host and not self.inGame:
          await self.init_game(sio)
          await self.run_game(sio)
          await self.finish_game(sio)
        elif cmd=='/투표' and self.STATE == 'VOTE':
          voter = self.players[user['nickname']]
          voted = self.players[target]
          to_send = {
            'voter': voter.nickname,
            'voted': voted.nickname
          }
          if await self.vote(voter, voted):
            await sio.emit('vote', to_send, room=self.roomID)
        elif cmd=='/유죄' and self.STATE == 'VOTE_EXECUTION':
          voter = self.players[user['nickname']]
          await self.vote_execution(voter, guilty=True)
        elif cmd=='/무죄' and self.STATE == 'VOTE_EXECUTION':
          voter = self.players[user['nickname']]
          await self.vote_execution(voter, guilty=False)
        elif cmd=='/취소':
          voter = self.players[user['nickname']]
          await self.cancel_vote(voter)
      else:
        to_send = {'who': user['nickname'],
                   'message': msg,}
        await sio.emit('message', to_send, room=self.roomID)

  async def vote(self, voter, voted):
    alive = len([p for p in self.players.values() if p.alive])
    majority = alive//2+1
    if voter.has_voted:
      return False
    voter.has_voted = True
    voted.votes_gotten += voter.votes
    voter.voted_to_whom = voted
    if voted.votes_gotten>=majority:
      self.elected = voted
      self.election.set()
    return True

  async def vote_execution(self, voter, guilty):
    if guilty:
      if not voter.has_voted_in_execution_vote:
        self.elected.voted_guilty += 1
        voter.has_voted_in_execution_vote = True
        self.voted_to_which = 'guilty'
    else:
      if not voter.has_voted_in_execution_vote:
        self.elected.voted_innocent += 1
        voter.has_voted_in_execution_vote = True
        self.voted_to_which = 'innocent'

  async def cancel_vote(self, voter):
    if self.STATE == 'VOTE':
      if voter.voted_to_whom is not None:
        voter.voted_to_whom.votes_gotten -= voter.votes
        voter.has_voted = False
        voter.voted_to_whom = None
    elif self.STATE == 'VOTE_EXECUTION':
      if voter.has_voted_in_execution_vote:
        voter.has_voted_in_execution_vote = False
        if voter.voted_to_which == 'guilty':
          self.elected.voted_innocent -= 1
        else:
          self.elected.voted_guilty -= 1
        voter.voted_to_which = None

  async def game_over(self):
    alive = [p for p in self.players.values() if p.alive]
    for p in alive:
      if p.role.team != alive[0].role.team:
        return False
    return True

  async def init_game(self, sio):
    # init game
    self.inGame = True
    self.election = asyncio.Event()
    if self.setup.get('default'):
      self.STATE = 'MORNING' # game's state when game starts
      self.MORNING_TIME = 5
      self.DISCUSSION_TIME = 10
      self.VOTE_TIME = 10
      self.DEFENSE_TIME = 10
      self.VOTE_EXECUTION_TIME = 10
      self.EVENING_TIME = 10
    roles_to_distribute = [roles.Mafioso(), roles.Citizen(), roles.Sheriff()]
    random.shuffle(roles_to_distribute)
    self.players = {(await sio.get_session(sid))['nickname']:
                    Player(sid=sid,
                           nickname=(await sio.get_session(sid))['nickname'],
                           role=roles_to_distribute[index])
                           for index, sid in enumerate(self.members)}
    for p in self.players.values():
      await sio.emit('role', p.role.name, room=p.sid)

  async def run_game(self, sio):
    while not await self.game_over():
      # MORNING
      self.STATE = 'MORNING'
      await sio.emit('state', self.STATE, room=self.roomID)
      await asyncio.sleep(self.MORNING_TIME)
      # DISCUSSION
      self.STATE = 'DISCUSSION'
      await sio.emit('state', self.STATE, room=self.roomID)
      await asyncio.sleep(self.DISCUSSION_TIME)
      # VOTE
      self.STATE = 'VOTE'
      await sio.emit('state', self.STATE, room=self.roomID)
      self.VOTE_ENDS_AT = datetime.now()+timedelta(seconds=self.VOTE_TIME)
      self.VOTE_TIME_REMAINING = (self.VOTE_ENDS_AT-datetime.now()).total_seconds()
      while self.VOTE_TIME_REMAINING>=0:
        try:
          await asyncio.wait_for(self.election.wait(), timeout=self.VOTE_TIME_REMAINING)
        except asyncio.TimeoutError: # nobody has been elected today
          break
        else: # someone has been elected
          self.STATE = 'DEFENSE'
          await sio.emit('state', self.STATE, room=self.roomID)
          await asyncio.sleep(self.DEFENSE_TIME)
          self.STATE = 'VOTE_EXECUTION'
          await sio.emit('state', self.STATE, room=self.roomID)
          await asyncio.sleep(self.VOTE_EXECUTION_TIME)
          if self.elected.voted_guilty>self.elected.voted_innocent:
            self.elected.die()
            break
          else:
            self.VOTE_TIME_REMAINING = (self.VOTE_ENDS_AT-datetime.now()).total_seconds()
            self.STATE = 'VOTE'
            await sio.emit('state', self.STATE, room=self.roomID)
        finally:
          self.election.clear()
          self.elected = None

      # EVENING
      self.STATE = 'EVENING'
      await sio.emit('state', self.STATE, room=self.roomID)
      await asyncio.sleep(self.EVENING_TIME)

      # NIGHT
      self.STATE = 'NIGHT'
      await sio.emit('state', self.STATE, room=self.roomID)

  async def finish_game(self, sio):
    self.inGame = False
    to_send = {
    'winner': [p.nickname for p in self.players.values() if p.alive]
    }
    await sio.emit('game_over', to_send,  room=self.roomID)


class Player:
  def __init__(self, sid, nickname, role):
    self.sid = sid
    self.nickname = nickname
    self.role = role
    self.alive = True
    self.votes = 1
    self.has_voted = False
    self.voted_to_whom = None
    self.has_voted_in_execution_vote = False
    self.voted_to_which = None
    self.votes_gotten = 0
    self.voted_guilty = 0
    self.voted_innocent = 0
    self.lw = '' # last will

  def die(self):
    self.alive = False
