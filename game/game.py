import random
import asyncio
from datetime import datetime, timedelta

from . import roles


class GameRoom:
    def __init__(self, roomID, title, capacity, host, setup,\
                 private=False, password=None):
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
                    data = {
                        'type': 'visit',
                        'role': visitor.role.name,
                        'target1': visitor.target1.nickname,
                        'target2': visitor.target2.nickname if visitor.target2 is not None else None
                    }
                    await sio.emit('event', data, room=visitor.sid)
                elif cmd == '/경계' and self.STATE =='EVENING':
                    V = self.players[user['nickname']]
                    V.alert_today = not V.alert_today
                    if V.alert_today:
                        V.role.defense_level = V.role.offense_level = 2
                    else:
                        V.role.defense_level = V.role.offense_level = 0
                    data = {
                        'type': 'alert',
                        'alert': V.alert_today,
                    }
                    await sio.emit('event', data, room=V.sid)
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

    def killable(self, attacker, attacked):
        return attacker.role.offense_level > attacked.role.defense_level

    async def emit_sound(self, sio, sound, dead=True):
        data = {
            'type': 'sound',
            'sound': sound,
            'dead': dead,
        }
        await sio.emit('event', data, room=self.roomID)

    async def trigger_night_events(self, sio):
        # 생존자 방탄 착용
        for p in self.alive_list:
            if isinstance(p.role, roles.Survivor) and p.wear_vest_today:
                p.defense_level = 1
                data = {
                    'type': 'wear_vest',
                }
                await sio.emit('event', data, room=p.sid)

        # 시민 방탄 착용
        for p in self.alive_list:
            if isinstance(p.role, roles.Citizen) and p.wear_vest_today:
                p.defense_level = 1
                data = {
                    'type': 'wear_vest',
                }
                await sio.emit('event', data, room=p.sid)

        # 마녀 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Witch)\
            and p.target1 is not None\
            and p.target2 is not None:
                if (isinstance(p.target1, roles.Veteran) and p.target1.alert_today)\
                or (isinstance(p.target1, roles.MassMurderer) and p.target1.murder_today):
                    continue
                else:
                    p.target1.target1 = p.target2
                    data = {
                        'type': 'Witch_control_success',
                    }
                    await sio.emit('event', data, room=p.sid)
                    data = {
                        'type': 'controlled_by_Witch',
                    }
                    await sio.emit('event', data, room=p.target1.sid)

        # 기생 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Escort)\
            and p.target1 is not None:
                p.target1.target1 = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {
                    'type': 'blocked'
                }
                await sio.emit('event', data, room=p.target1.sid)

        # 매춘부 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Consort)\
            and p.target1 is not None:
                p.target1.target1 = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {
                    'type': 'blocked'
                }
                await sio.emit('event', data, room=p.target1.sid)

        # 간통범 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Liaison)\
            and p.target1 is not None:
                p.target1.target1 = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {
                    'type': 'blocked'
                }
                await sio.emit('event', data, room=p.target1.sid)

        # 잠입자 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Beguiler)\
            and p.target1 is not None:
                for p2 in self.alive_list:
                    if p2.target1 is p:
                        p2.target1 = p.target1

        # 사기꾼 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Deceiver)\
            and p.target1 is not None:
                for p2 in self.alive_list:
                    if p2.target1 is p:
                        p2.target1 = p.target1

        # 방문자 모두 확정되면 방문자 목록에 추가
        for p in self.alive_list:
            if p.target1 is not None:
                p.target1.visited_by[self.day].add(p)

        # 방화범 기름칠 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Arsonist) and not p.burn_today\
            and p.target1 is not None:
                p.target1.oiled = True
                data = {
                    'type': 'oiling_success',
                }
                await sio.emit('event', data, room=p.sid)

        # 의사 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Doctor)\
            and p.target1 is not None:
                p.target1.healed_by.append(p)

        # 경호원 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Bodyguard)\
            and p.target1 is not None:
                p.target1.bodyguarded_by.append(p)

        self.die_today = set()
        # 경계 중인 퇴역군인에게 간 애들부터 죽는다.
        for p in self.alive_list:
            if p.target1 is None:
                continue
            if isinstance(p.target1.role, roles.Veteran)\
            and p.target1.alert_today:
                V = p.target1 # V stands for Veteran
                if isinstance(p.role, roles.Bodyguard):
                    V.bodyguarded_by.remove(p)
                if isinstance(p.role, roles.Doctor)\
                or isinstance(p.role, roles.WitchDoctor):
                    V.healed_by.remove(p)
                data = {
                    'type': 'someone_visited_to_Veteran'
                }
                await sio.emit('event', data, room=V.sid)
                data = {
                    'type': 'visited_Veteran',
                    'with_Bodyguard': len(p.bodyguarded_by) != 0,
                }
                await sio.emit('event', data, room=p.sid)
                if self.killable(V, p):
                    if p.bodyguarded_by:
                        BG = p.bodyguarded_by.pop() # BG stands for Bodyguard
                        await p.bodyguarded(attacker=V)
                        data = {
                            'type': 'fighted_with_Bodyguard'
                        }
                        await sio.emit('event', data, room=V.sid)
                        await self.emit_sound(sio, 'Bodyguard')
                        if BG.healed_by:
                            H = BG.healed_by.pop()
                            await BG.healed(attacker=V, healer=H)
                        else:
                            await BG.die(attacker=V, dead_while_guarding=True)
                    elif p.healed_by:
                        H = p.healed_by.pop()
                        await self.emit_sound(sio, 'Veteran')
                        await p.healed(attacker=V, healer=H)
                    else:
                        await self.emit_sound(sio, 'Veteran')
                        await p.die(attacker=V)
                else:
                    await self.emit_sound(sio, 'Veteran', dead=False)
                    await p.attacked(attacker=V)

        # 간수의 처형대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Jailor)\
            and p.kill_the_jailed_today:
                await self.emit_sound(sio, 'Jailor')
                await p.has_jailed_whom.die(attacker=p)

        # 납치범의 처형대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Kidnapper)\
            and p.kill_the_jailed_today:
                await self.emit_sound(sio, 'Jailor')
                await p.has_jailed_whom.die(attacker=p)

        # 심문자의 처형대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Interrogator)\
            and p.kill_the_jailed_today:
                await self.emit_sound(sio, 'Jailor')
                await p.has_jailed_whom.die(attacker=p)

        # 자경대원의 대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Vigilante) and p.target1 is not None:
                victim = p.target1
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, 'Suicide_by_control')
                    else:
                        data = {
                            'type': 'almost_suicide'
                        }
                        await sio.emit('event', data, room=p.sid)
                    continue
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop() # BG stands for Bodyguard
                    await victim.bodyguarded(attacker=p)
                    await self.emit_sound(sio, 'Bodyguard')
                    if p.healed_by:
                        H = p.healed_by.pop() # H stands for Healer
                        await p.healed(attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG)
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True)
                elif self.killable(p, victim):
                    await self.emit_sound(sio, 'Vigilante')
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await P.healed(attacker=p, healer = H)
                    else:
                        await victim.die(attacker=p)
                else:
                    await self.emit_sound(sio, 'Vigilante', dead=False)
                    await victim.attacked(attacker=p)

        # 마피아의 대상이 죽는다.
        for p in self.alive_list:
            if (isinstance(p.role, roles.Godfather)\
            or isinstance(p.role, roles.Mafioso))\
            and p.target1 is not None:
                victim = p.target1
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, 'Suicide_by_control')
                    else:
                        data = {
                            'type': 'almost_suicide'
                        }
                        await sio.emit('event', data, room=p.sid)
                elif isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                elif victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop() # BG stands for Bodyguard
                    await victim.bodyguarded(attacker=p)
                    await self.emit_sound(sio, 'Bodyguard')
                    if p.healed_by:
                        H = p.healed_by.pop() # H stands for Healer
                        await p.healed(attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG)
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True)
                elif self.killable(p, victim):
                    await self.emit_sound(sio, 'Mafioso')
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await P.healed(attacker=p, healer = H)
                    else:
                        await victim.die(attacker=p)
                else:
                    await self.emit_sound(sio, 'Mafioso', dead=False)
                    await victim.attacked(attacker=p)

        # 삼합회의 대상이 죽는다.
        for p in self.alive_list:
            if (isinstance(p.role, roles.DragonHead)\
            or isinstance(p.role, roles.Enforcer))\
            and p.target1 is not None:
                victim = p.target1
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, 'Suicide_by_control')
                    else:
                        data = {
                            'type': 'almost_suicide'
                        }
                        await sio.emit('event', data, room=p.sid)
                elif isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                elif victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop() # BG stands for Bodyguard
                    await victim.bodyguarded(attacker=p)
                    await self.emit_sound(sio, 'Bodyguard')
                    if p.healed_by:
                        H = p.healed_by.pop() # H stands for Healer
                        await p.healed(attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG)
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True)
                elif self.killable(p, victim):
                    await self.emit_sound(sio, 'Mafioso')
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await P.healed(attacker=p, healer = H)
                    else:
                        await victim.die(attacker=p)
                else:
                    await self.emit_sound(sio, 'Mafioso', dead=False)
                    await victim.attacked(attacker=p)

        # 연쇄살인마의 대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.SerialKiller) and p.target1 is not None:
                victim = p.target1
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, 'Suicide_by_control')
                    else:
                        data = {
                            'type': 'almost_suicide'
                        }
                        await sio.emit('event', data, room=p.sid)
                elif isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                elif victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop() # BG stands for Bodyguard
                    await victim.bodyguarded(attacker=p)
                    await self.emit_sound(sio, 'Bodyguard')
                    if p.healed_by:
                        H = p.healed_by.pop() # H stands for Healer
                        await p.healed(attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG)
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True)
                elif self.killable(p, victim):
                    await self.emit_sound(sio, 'SerialKiller')
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await P.healed(attacker=p, healer = H)
                    else:
                        await victim.die(attacker=p)
                else:
                    await self.emit_sound(sio, 'SerialKiller', dead=False)
                    await victim.attacked(attacker=p)

        # 방화범이 불을 피운다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Arsonist) and p.burn_today:
                for victim in self.alive_list:
                    if victim.oiled:
                        if self.killable(p, victim):
                            if victim.healed_by:
                                H = victim.healed_by.pop()
                                victim.healed(attacker=p, healer=H)
                            else:
                                victim.die(attacked=p)
                        if victim.target1 is not None and self.killable(p, victim.target1):
                            victim2 = victim.target1
                            if victim2.healed_by:
                                H = victim2.healed_by.pop()
                                victim2.healed(attacker=p, healer=H)
                            else:
                                victim2.die(attacked=p)

        # 비밀조합장의 살인 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.MasonLeader) and victim is not None\
            and isinstance(victim, roles.Cult):
                victim = victim
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()
                    await victim.bodyguarded(attacker=p)
                    if p.healed_by:
                        H = p.healed_by.pop()
                        await p.healed(attacker=BG, healer=H)
                    else:
                        await p.die(attacker=BG)
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(attacker=p)
                    else:
                        BG.die(attacker=p, dead_while_guarding=True)
                elif victim.healed_by:
                    H = victim.healed_by.pop()
                    await victim.healed(attacker=p, healer=H)
                else:
                    await victim.die(attacker=p)

        # 대량학살자 살인 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.MassMurderer) and p.murder_today is not None\
            and p.target1 is not None:
                victims = [v for v in self.alive_list if v.target1 is p.target1\
                           or (isinstance(v.role, roles.Bodyguard) and v.target1 is p)]
                for v in victims:
                    if v.bodyguarded_by:
                        BG = v.bodyguarded_by.pop()
                        await p.die(attacker=BG)
                        await v.bodyguarded(attacker=p)
                    elif not self.killable(p, v):
                        await v.attacked(attacker=p)
                    elif v.healed_by:
                        H = v.healed_by.pop()
                        await v.healed(attacker=p, healer=H)
                    else:
                        await v.die(attacker=p)

        # 어릿광대 자살 적용
        candidates = [p for p in self.alive_list if p.voted_to_execution_of_jester]
        random.shuffle(candidates)
        if candidates:
            victim = candidates.pop()
            if victim.healed_by:
                H = victim.healed_by.pop()
                class Dummy: # dummy class
                    pass
                dummy = Dummy()
                dummy.role = Dummy()
                dummy.role.name = '어릿광대'
                await victim.healed(attacker=dummy, healer=H)
            else:
                await victim.suicide(reason=roles.Jester.name)

        # TODO: 심장마비 자살
        # TODO: 변장자
        # TODO: 밀고자

        # 고의 자살 적용
        for p in self.alive_list:
            if p.suicide_today:
                if p.healed_by:
                    H = p.healed_by.pop()
                    class Dummy: # dummy class
                        pass
                    dummy = Dummy()
                    dummy.role = Dummy()
                    dummy.role.name = '자살'
                    await victim.healed(attacker=dummy, healer=H)
                else:
                    await victim.suicide(reason='고의')

        # 마녀 저주 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Witch)\
            and p.curse_target is not None and not p.has_cursed:
                victim = p.curse_target
                if victim.healed_by:
                    H = victim.healed_by.pop()
                    await victim.healed(attacker=p, healer=H)
                else:
                    await victim.die(attacker=p)

        # 사망자들 제거
        for dead in self.die_today:
            self.alive_list.remove(dead)

        # TODO: 관리인/향주 직업 수거
        # TODO: 조작자/위조꾼

        # 조사직들 능력 발동
        for p in self.alive_list:
            for investigating_role in (roles.TownInvestigative,
                                       roles.Consigliere,
                                       roles.Administrator):
                if isinstance(p.role, investigating_role) and p.target1 is not None:
                    result = p.role.check(p.target1)
                    data = {
                        'type': 'check_result',
                        'role': p.role.name,
                        'result': result,
                    }
                    await sio.emit('event', data, room=p.sid)

        # TODO: 변장자 이동
        # TODO: 어릿광대 괴롭히기
        # TODO: 회계사 회계
        # TODO: 비밀조합 영입
        # TODO: 이교도 개종
        # TODO: 마피아/삼합회 영입


    async def clear_up(self):
        for p in self.alive_list:
            p.has_voted = False
            p.voted_to_whom = None
            p.voted_to_execution_of_jester = False
            p.has_voted_in_execution_vote = False
            p.voted_to_which = None
            p.votes_gotten = 0
            p.voted_guilty = 0
            p.voted_innocent = 0
            p.visited_by.append(set())
            p.wear_vest_today = False
            p.alert_today = False
            p.burn_today = False
            p.curse_today = False
            p.suicide_today = False
            p.protected_from_cult = False
            p.protected_from_auditor = False
            p.kill_the_jailed_today = False
            p.jailed = False
            p.bodyguarded_by = []
            p.healed_by = []
            p.target1 = None
            p.target2 = None
            p.curse_target = None
            p.has_jailed_whom = None

    def game_over(self):
        for p in self.alive_list:
            if p.role.team != self.alive_list[0].role.team:
                return False
        return True

    async def init_game(self, sio):
        # init game
        print('Game initiated in room #', self.roomID)
        self.inGame = True
        self.election = asyncio.Event()
        self.day = 0
        if self.setup.get('default'):
            self.STATE = 'MORNING'  # game's first state when game starts
            self.MORNING_TIME = 5
            self.DISCUSSION_TIME = 10
            self.VOTE_TIME = 10
            self.DEFENSE_TIME = 10
            self.VOTE_EXECUTION_TIME = 10
            self.EVENING_TIME = 30
        roles_to_distribute = [roles.Bodyguard(),
                               roles.Veteran(),
                               roles.Mafioso(),
                               roles.Escort(),
                               roles.Beguiler(),
                               roles.SerialKiller(),]
        # random.shuffle(roles_to_distribute)
        self.players = {(await sio.get_session(sid))['nickname']:
                        Player(sid=sid,
                               room=self,
                               nickname=(await sio.get_session(sid))['nickname'],
                               role=roles_to_distribute[index],
                               sio=sio)
                        for index, sid in enumerate(self.members)}
        self.alive_list = list(self.players.values())
        for p in self.players.values():
            data = {
                'type': 'role',
                'role': p.role.name,
            }
            await sio.emit('event', data, room=p.sid)

    async def run_game(self, sio):
        print('Game starts in room #', self.roomID)
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
                    await asyncio.wait_for(self.election.wait(),
                                           timeout=self.VOTE_TIME_REMAINING)
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
                        self.elected.die(attacker='Vote')
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

            if self.game_over():
                return
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
            await self.clear_up()

    async def finish_game(self, sio):
        print('Game fininshed in room #', self.roomID)
        self.inGame = False
        to_send = {
            'type': 'game_over',
            'winner': [p.nickname for p in self.alive_list]
        }
        await sio.emit('event', to_send,  room=self.roomID)


class Player:
    def __init__(self, sid, room, nickname, role, sio):
        self.sid = sid
        self.room = room
        self.nickname = nickname
        self.role = role
        self.sio = sio
        self.alive = True
        self.votes = 1
        self.has_voted = False
        self.voted_to_whom = None
        self.voted_to_execution_of_jester = False
        self.has_voted_in_execution_vote = False
        self.voted_to_which = None
        self.votes_gotten = 0
        self.voted_guilty = 0
        self.voted_innocent = 0
        self.lw = ''  # last will
        self.visited_by = [None, set()]
        self.wear_vest_today = False
        self.alert_today = False
        self.burn_today = False
        self.curse_today = False
        self.suicide_today = False
        self.protected_from_cult = False
        self.protected_from_auditor = False
        self.kill_the_jailed_today = False
        self.oiled = False
        self.jailed = False
        self.has_disguised = False
        self.has_cursed = False
        self.bodyguarded_by = [] # list of Player objects
        self.healed_by = [] # list of Player objects
        self.target1 = None
        self.target2 = None
        self.curse_target = None
        self.has_jailed_whom = None
        self.crimes = set()

    async def die(self, attacker, dead_while_guarding=False):
        self.room.die_today.add(self)
        self.alive = False
        data = {
            'type': 'dead',
            'attacker': attacker.role.name,
            'dead_while_guarding': dead_while_guarding,
        }
        await self.sio.emit('event', data, room=self.sid)

    async def attacked(self, attacker):
        data = {
            'type': 'attacked',
            'attacker': attacker.role.name,
        }
        await self.sio.emit('event', data, room=self.sid)

    async def healed(self, attacker, healer):
        data = {
            'type': 'healed',
            'attacker': attacker.role.name,
            'healer': healer.role.name,
        }
        await self.sio.emit('event', data, room=self.sid)

    async def bodyguarded(self, attacker):
        data = {
            'type': 'bodyguarded',
            'attacker': attacker.role.name,
        }
        await self.sio.emit('event', data, room=self.sid)

    async def suicide(self, reason):
        data = {
            'type': 'suicide',
            'reason': reason,
        }
        await self.sio.emit('event', data, room=self.sid)
