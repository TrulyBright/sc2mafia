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
        return len(self.members) >= self.capacity

    async def handle_message(self, sio, sid, msg):
        async with sio.session(sid) as user:
            if msg.startswith('/'):
                msg = msg.split()
                if len(msg) == 3:
                    cmd, target1, target2 = msg
                    if target1 not in self.players:
                        return
                    if target2 not in self.players:
                        return
                elif len(msg) == 2:
                    cmd, target1 = msg
                    target2 = None
                    if target1 not in self.players:
                        return
                else:
                    cmd = msg[0]
                    target1 = target2 = None
                if cmd == '/시작' and sid == self.host and not self.inGame:
                    await self.init_game(sio)
                    await self.run_game(sio)
                    await self.finish_game(sio)
                elif cmd == '/투표' and self.STATE == 'VOTE' and target1:
                    voter = self.players[user['nickname']]
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            'type': 'vote_cancel',
                            'voter': voter.nickname,
                        }
                        await sio.emit('event', data, room=self.roomID)
                    else:
                        voted = self.players[target1]
                        data = {
                            'type': 'vote',
                            'voter': voter.nickname,
                            'voted': voted.nickname,
                        }
                        self.vote(voter, voted)
                        await sio.emit('event', data, room=self.roomID)
                elif cmd == '/유죄' and self.STATE == 'VOTE_EXECUTION':
                    voter = self.players[user['nickname']]
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            'type': 'vote_cancel',
                            'voter': voter.nickname,
                        }
                        await sio.emit('vote_cancel', data, room=self.roomID)
                    else:
                        await self.vote_execution(voter, guilty=True)
                        data = {
                            'type': 'vote_execution',
                            'voter': voter.nickname,
                        }
                        await sio.emit('event', data, room=self.roomID)
                elif cmd == '/무죄' and self.STATE == 'VOTE_EXECUTION':
                    voter = self.players[user['nickname']]
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            'type': 'vote_cancel',
                            'voter': voter.nickname,
                        }
                        await sio.emit('event', data, room=self.roomID)
                    else:
                        self.vote_execution(voter, guilty=False)
                        data = {
                            'type': 'vote_execution',
                            'voter': voter.nickname,
                        }
                        await sio.emit('event', data, room=self.roomID)
                elif cmd == '/방문' and self.STATE == 'EVENING' and target1:
                    visitor = self.players[user['nickname']]
                    visited = self.players[target1]
                    visitor.target1 = visited
                    if target2 is not None:
                        visitor.target2 = self.players[user[target2]]
            else:
                to_send = {'who': user['nickname'],
                           'message': msg, }
                await sio.emit('message', to_send, room=self.roomID)

    def vote(self, voter, voted):
        assert self.STATE == 'VOTE'
        alive = len([p for p in self.players.values() if p.alive])
        majority = alive//2+1
        voter.has_voted = True
        voted.votes_gotten += voter.votes
        voter.voted_to_whom = voted
        if voted.votes_gotten >= majority:
            self.elected = voted
            self.election.set()

    def vote_execution(self, voter, guilty):
        assert self.STATE == 'VOTE_EXECUTION'
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

    def cancel_vote(self, voter):
        assert self.STATE in ('VOTE', 'VOTE_EXECUTION')
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

    async def trigger_night_events(self, sio):
        for p in self.players:
            if isinstance(p.role, roles.Citizen) and p.wear_vest_today:
                p.role.defense_level = 1

        for p in self.players:
            if isinstance(p.role, roles.Veteran) and p.alert_today:
                p.role.defense_level = 2

        for p in self.players:
            if isinstance(p.role, roles.Witch) and p.target1 is not None and p.target2 is not None:
                if isinstance(p.role, roles.Veteran):
                    p.die()
                    data = {
                        'type': 'dead',
                        'reason': 'Veteran'
                    }
                    await sio.emit('event', data, room=p.sid)
                else:
                    p.target1.target1 = p.target2
                    data = {
                        'type': 'result',
                        'role': 'role'
                    }

        for p in self.players:
            if type(p.role) == roles.Escort and p.target1 is not None:
                p.target1.target1 = None

    def game_over(self):
        alive = [p for p in self.players.values() if p.alive]
        for p in alive:
            if p.role.team != alive[0].role.team:
                return False
        return True

    async def init_game(self, sio):
        # init game
        self.inGame = True
        self.election = asyncio.Event()
        self.day = 0
        self.night_triggers = {
            roles.Citizen: set(),
            roles.Witch: set(),
            roles.Mafioso: set(),
            roles.Sheriff: set(),
        }
        if self.setup.get('default'):
            self.STATE = 'MORNING'  # game's state when game starts
            self.MORNING_TIME = 5
            self.DISCUSSION_TIME = 10
            self.VOTE_TIME = 10
            self.DEFENSE_TIME = 10
            self.VOTE_EXECUTION_TIME = 10
            self.EVENING_TIME = 10
        roles_to_distribute = [
            roles.Mafioso(), roles.Citizen(), roles.Sheriff()]
        random.shuffle(roles_to_distribute)
        self.players = {(await sio.get_session(sid))['nickname']:
                        Player(sid=sid,
                               nickname=(await sio.get_session(sid))['nickname'],
                               role=roles_to_distribute[index])
                        for index, sid in enumerate(self.members)}
        for p in self.players.values():
            await sio.emit('role', p.role.name, room=p.sid)

    async def run_game(self, sio):
        while not self.game_over():
            self.day += 1
            # MORNING
            self.STATE = 'MORNING'
            data = {
                'type': 'state',
                'state': self.STATE,
            }
            await sio.emit('event', data, room=self.roomID)
            await asyncio.sleep(self.MORNING_TIME)
            # DISCUSSION
            self.STATE = 'DISCUSSION'
            data = {
                'type': 'state',
                'state': self.STATE,
            }
            await sio.emit('event', data, room=self.roomID)
            await asyncio.sleep(self.DISCUSSION_TIME)
            # VOTE
            self.STATE = 'VOTE'
            data = {
                'type': 'state',
                'state': self.STATE,
            }
            await sio.emit('event', data, room=self.roomID)
            self.VOTE_ENDS_AT = datetime.now()+timedelta(seconds=self.VOTE_TIME)
            self.VOTE_TIME_REMAINING = (
                self.VOTE_ENDS_AT-datetime.now()).total_seconds()
            while self.VOTE_TIME_REMAINING >= 0:
                try:
                    await asyncio.wait_for(self.election.wait(), timeout=self.VOTE_TIME_REMAINING)
                except asyncio.TimeoutError:  # nobody has been elected today
                    break
                else:  # someone has been elected
                    self.STATE = 'DEFENSE'
                    data = {
                        'type': 'state',
                        'state': self.STATE,
                    }
                    await sio.emit('event', data, room=self.roomID)
                    await asyncio.sleep(self.DEFENSE_TIME)
                    self.STATE = 'VOTE_EXECUTION'
                    data = {
                        'type': 'state',
                        'state': self.STATE,
                    }
                    await sio.emit('event', data, room=self.roomID)
                    await asyncio.sleep(self.VOTE_EXECUTION_TIME)
                    if self.elected.voted_guilty > self.elected.voted_innocent:
                        self.elected.die()
                        data = {
                            'type': 'dead',
                            'reason': 'vote',
                        }
                        await sio.emit('event', data, room=self.elected.sid)
                        break
                    else:
                        self.VOTE_TIME_REMAINING = (
                            self.VOTE_ENDS_AT-datetime.now()).total_seconds()
                        self.STATE = 'VOTE'
                        data = {
                            'type': 'state',
                            'state': self.STATE,
                        }
                        await sio.emit('event', self.STATE, room=self.roomID)
                finally:
                    self.election.clear()
                    self.elected = None

            # EVENING
            self.STATE = 'EVENING'
            data = {
                'type': 'state',
                'state': self.STATE,
            }
            await sio.emit('event', data, room=self.roomID)
            await asyncio.sleep(self.EVENING_TIME)

            # NIGHT
            self.STATE = 'NIGHT'
            data = {
                'type': 'state',
                'state': self.STATE,
            }
            await sio.emit('event', data, room=self.roomID)
            await self.trigger_night_events(sio)

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
        self.lw = ''  # last will
        self.visited_by = [[], []]
        self.wear_vest_today = False
        self.alert_today = False
        self.target1 = None
        self.target2 = None

    def die(self):
        self.alive = False
