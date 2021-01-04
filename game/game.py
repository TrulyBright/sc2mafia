import random
import asyncio
import aiosqlite
import random
import time
import string
import json
import sqlite3
from datetime import datetime, timedelta

from . import roles


class GameRoom:
    def __init__(
        self, roomID, title, capacity, host, setup, private=False, password=None
    ):
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
        self.message_record = []

    def is_full(self):
        return len(self.members) >= self.capacity

    def write_to_record(self, sio, data, room, skip_sid):
        if not self.inGame:
            return
        receivers = [p.nickname for p in self.players.values() if room in sio.rooms(p.sid)]
        self.message_record.append((time.time(), str(data), str(receivers)))

    async def emit_event(self, sio, data, room, skip_sid=None):
        await sio.emit("event", data, room=room, skip_sid=skip_sid)
        self.write_to_record(sio, data, room, skip_sid)

    async def handle_message(self, sio, sid, msg):
        async with sio.session(sid) as user:
            if not self.inGame:
                if msg == "/시작" and sid == self.host:
                    await self.init_game(sio)
                    await self.run_game(sio)
                    await self.finish_game(sio)
                else:
                    data = {
                        "type": "message",
                        "who": user["nickname"],
                        "message": msg,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                return
            if user["nickname"] not in self.players: # 나중에 들어온 사람일 경우: HellID에 입장한 상태임.
                data = {
                    "type": "message",
                    "who": user["nickname"],
                    "message": msg,
                    "hell": True,
                }
                await self.emit_event(sio, data, room=self.hellID)
                return

            commander = self.players[user["nickname"]]
            if msg.startswith("/"):
                if commander.jailed:
                    return
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
                if target1 and commander is self.players[target1] and not commander.role.visitable_himself:
                    return
                elif cmd == "/투표" and self.STATE == "VOTE" and target1:
                    voter = commander
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            "type": "vote_cancel",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                    else:
                        voted = self.players[target1]
                        data = {
                            "type": "vote",
                            "voter": voter.nickname,
                            "voted": voted.nickname,
                        }
                        self.vote(voter, voted)
                        await self.emit_event(sio, data, room=self.roomID)
                elif cmd == "/유죄" and self.STATE == "VOTE_EXECUTION":
                    voter = commander
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            "type": "vote_cancel",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                    else:
                        self.vote_execution(voter, guilty=True)
                        data = {
                            "type": "vote_execution",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                elif cmd == "/무죄" and self.STATE == "VOTE_EXECUTION":
                    voter = commander
                    if not voter.alive:
                        return
                    if voter.has_voted:
                        self.cancel_vote(voter)
                        data = {
                            "type": "vote_cancel",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                    else:
                        self.vote_execution(voter, guilty=False)
                        data = {
                            "type": "vote_execution",
                            "voter": voter.nickname,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                elif (
                    cmd == "/방문"
                    and commander.alive
                    and self.STATE == "EVENING"
                    and target1
                ):
                    visitor = commander
                    visited = self.players[target1]
                    if (
                        isinstance(visitor.role, roles.MassMurderer)
                        and visitor.cannot_murder_until >= self.day
                    ):
                        return
                    visitor.target1 = visited
                    if target2 and (
                        isinstance(visitor.role, roles.Witch)
                        or isinstance(visitor.role, roles.BusDriver)
                    ):
                        visitor.target2 = self.players[target2]
                    data = {
                        "type": "visit",
                        "role": visitor.role.name,
                        "target1": visitor.target1.nickname,
                        "target2": visitor.target2.nickname
                        if visitor.target2
                        else None,
                    }
                    if isinstance(visitor.role, roles.Mafia):
                        await self.emit_event(sio, data, room=self.mafiaChatID)
                    elif isinstance(visitor.role, roles.Triad):
                        await self.emit_event(sio, data, room=self.triadChatID)
                    elif isinstance(visitor.role, roles.Cult):
                        await self.emit_event(sio, data, room=self.cultChatID)
                    elif isinstance(visitor.role, roles.Mason) or isinstance(
                        visitor.role, roles.MasonLeader
                    ):
                        await self.emit_event(sio, data, room=self.masonChatID)
                    else:
                        await self.emit_event(sio, data, room=visitor.sid)
                elif (
                    cmd == "/경계"
                    and self.STATE == "EVENING"
                    and isinstance(commander.role, roles.Veteran)
                ):
                    V = commander
                    V.alert_today = not V.alert_today
                    if V.alert_today:
                        V.role.defense_level = V.role.offense_level = 2
                    else:
                        V.role.defense_level = V.role.offense_level = 0
                    data = {
                        "type": "alert",
                        "alert": V.alert_today,
                    }
                    await self.emit_event(sio, data, room=V.sid)
                elif (
                    cmd == "/착용"
                    and commander.alive
                    and self.STATE == "EVENING"
                    and (
                        isinstance(commander.role, roles.Citizen)
                        or isinstance(commander.role, roles.Survivor)
                    )
                ):
                    wearer = commander
                    wearer.wear_vest_today = not wearer.wear_vest_today
                    if wearer.wear_vest_today:
                        wearer.role.defense_level = 1
                    else:
                        wearer.role.defense_level = 0
                    data = {"type": "wear_vest", "wear_vest": wearer.wear_vest_today}
                    await self.emit_event(sio, data, room=wearer.sid)
                elif (
                    cmd == "/감금"
                    and commander.alive
                    and self.STATE != "EVENING"
                    and self.STATE != "NIGHT"
                    and target1
                    and (
                        isinstance(commander.role, roles.Jailor)
                        or isinstance(commander.role, roles.Kidnapper)
                        or isinstance(commander.role, roles.Interrogator)
                    )
                ):
                    jailor = commander
                    to_jail = self.players[target1]
                    jailor.has_jailed_whom = to_jail
                    data = {
                        "type": "will_jail",
                        "whom": to_jail.nickname,
                    }
                    await self.emit_event(sio, data, room=commander.sid)
                elif (
                    cmd == "/영입"
                    and commander.alive
                    and self.STATE == "EVENING"
                    and target1
                    and (
                        isinstance(commander.role, roles.Godfather)
                        or isinstance(commander.role, roles.DragonHead)
                    )
                ):
                    recruiter = commander
                    recruited = self.players[target1]
                    recruiter.recruit_target = recruited
                    data = {
                        "type": "will_recruit",
                        "recruited": recruited.nickname,
                    }
                    if isinstance(commander.role, roles.Godfather):
                        await self.emit_event(sio, data, room=self.mafiaChatID)
                    else:
                        await self.emit_event(sio, data, room=self.triadChatID)
                elif cmd == "/처형" and commander.alive and self.STATE == "EVENING":
                    if (
                        isinstance(commander.role, roles.Jailor)
                        and commander.has_jailed_whom
                        and commander.role.ability_opportunity > 0
                    ):
                        commander.kill_the_jailed_today = (
                            not commander.kill_the_jailed_today
                        )
                        if commander.kill_the_jailed_today:
                            data = {
                                "type": "will_execute",
                                "executed": commander.has_jailed_whom.nickname,
                            }
                            await self.emit_event(sio, data, room=commander.has_jailed_whom.jailID)
                        else:
                            data = {
                                "type": "will_not_execute",
                            }
                            await self.emit_event(sio, data, room=commander.has_jailed_whom.jailID)
                    elif (
                        isinstance(commander.role, roles.Kidnapper)
                        or isinstance(commander.role, roles.Interrogator)
                    ) and commander.has_jailed_whom:
                        commander.kill_the_jailed_today = (
                            not commander.kill_the_jailed_today
                        )
                        if commander.kill_the_jailed_today:
                            data = {
                                "type": "will_execute",
                                "executed": commander.has_jailed_whom.nickname,
                            }
                            await self.emit_event(sio, data, room=commander.has_jailed_whom.jailID)
                        else:
                            data = {
                                "type": "will_not_execute",
                            }
                            await self.emit_events(sio, data, room=commander.has_jailed_whom.jailID)
            else:
                if commander not in self.alive_list:
                    data = {
                        "type": "message",
                        "who": user["nickname"],
                        "message": msg,
                        "hell": True,
                    }
                    await self.emit_event(sio, data, room=self.hellID)
                elif self.STATE == "NIGHT":
                    return
                elif self.STATE == "EVENING":
                    player = commander
                    if player.jailed:
                        data = {
                            "type": "message",
                            "who": player.nickname,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.jailID)
                    elif (
                        isinstance(player.role, roles.Jailor) and player.has_jailed_whom
                    ):
                        data = {
                            "type": "message",
                            "who": roles.Jailor.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.has_jailed_whom.jailID)
                    elif (
                        isinstance(player.role, roles.Kidnapper)
                        and player.has_jailed_whom
                    ):
                        skip_list = [
                            p.sid
                            for p in self.alive_list
                            if isinstance(p.role, roles.Mafia)
                        ]
                        data = {
                            "type": "message",
                            "who": roles.Jailor.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.has_jailed_whom.jailID, skip_sid=skip_list)
                        data["who"] = player.nickname
                        await self.emit_event(sio, data, room=self.mafiaChatID)
                    elif (
                        isinstance(player.role, roles.Interrogator)
                        and player.has_jailed_whom
                    ):
                        skip_list = [
                            p.sid
                            for p in self.alive_list
                            if isinstance(p.role, roles.Triad)
                        ]
                        data = {
                            "type": "message",
                            "who": roles.Jailor.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=player.has_jailed_whom.jailID, skip_sid=skip_list)
                        data["who"] = player.nickname
                        await self.emit_event(sio, data, room=self.triadChatID)
                    elif isinstance(player.role, roles.Judge) or isinstance(
                        player.role, roles.Crier
                    ):
                        data = {
                            "type": "message",
                            "who": roles.Crier.name,
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                        player.crimes["치안을 어지럽힘"] = True
                    elif isinstance(player.role, roles.Mafia):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.mafiaChatID)
                        data["who"] = roles.Mafia.team
                        await self.emit_event(sio, data, room=self.spyRoomID)
                    elif isinstance(player.role, roles.Triad):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.triadChatID)
                        data["who"] = roles.Triad.team
                        await self.emit_event(sio, data, room=self.spyRoomID)
                    elif isinstance(player.role, roles.Cult):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.cultChatID)
                    elif isinstance(player.role, roles.Mason) or isinstance(
                        player.role, roles.MasonLeader
                    ):
                        data = {
                            "type": "message",
                            "who": user["nickname"],
                            "message": msg,
                        }
                        await self.emit_event(sio, data, room=self.masonChatID)
                else:
                    data = {
                        "type": "message",
                        "who": user["nickname"],
                        "message": msg,
                    }
                    await self.emit_event(sio, data, room=self.roomID)

    def vote(self, voter, voted):
        assert self.STATE == "VOTE"
        alive = len([p for p in self.players.values() if p.alive])
        majority = alive // 2 + 1
        voter.has_voted = True
        voted.votes_gotten += voter.votes
        voter.voted_to_whom = voted
        if voted.votes_gotten >= majority:
            self.elected = voted
            self.election.set()

    def vote_execution(self, voter, guilty):
        assert self.STATE == "VOTE_EXECUTION"
        if guilty:
            if not voter.has_voted_in_execution_vote:
                self.elected.voted_guilty += 1
                voter.has_voted_in_execution_vote = True
                self.voted_to_which = "guilty"
        else:
            if not voter.has_voted_in_execution_vote:
                self.elected.voted_innocent += 1
                voter.has_voted_in_execution_vote = True
                self.voted_to_which = "innocent"

    def cancel_vote(self, voter):
        assert self.STATE in ("VOTE", "VOTE_EXECUTION")
        if self.STATE == "VOTE":
            if voter.voted_to_whom:
                voter.voted_to_whom.votes_gotten -= voter.votes
                voter.has_voted = False
                voter.voted_to_whom = None
        elif self.STATE == "VOTE_EXECUTION":
            if voter.has_voted_in_execution_vote:
                voter.has_voted_in_execution_vote = False
                if voter.voted_to_which == "guilty":
                    self.elected.voted_innocent -= 1
                else:
                    self.elected.voted_guilty -= 1
                voter.voted_to_which = None

    def killable(self, attacker, attacked):
        return attacker.role.offense_level > attacked.role.defense_level

    async def emit_sound(self, sio, sound, dead=True, number_of_murdered=1):
        data = {
            "type": "sound",
            "sound": sound,
            "dead": dead,
            "number_of_murdered": number_of_murdered,
        }
        await self.emit_event(sio, data, room=self.roomID)

    async def convert_role(self, sio, convertor, converted, role):
        if convertor.nightChatID:
            sio.leave_room(converted.sid, convertor.nightChatID)
            convertor.nightChatID = None
        converted.role = role
        converted.role_record.append(role)
        data = {
            "type": "role_converted",
            "role": role.name,
            "convertor": convertor.role.name if convertor else None,
        }
        await self.emit_event(sio, data, room=converted.sid)
        if isinstance(converted.role, roles.Mafia):
            sio.enter_room(converted.sid, self.mafiaChatID)
        elif isinstance(converted.role, roles.Triad):
            sio.enter_room(converted.sid, self.triadChatID)
        elif isinstance(converted.role, roles.Cult):
            sio.enter_room(converted.sid, self.cultChatID)
        elif isinstance(converted.role, roles.Mason):
            sio.enter_room(converted.sid, self.masonChatID)

    async def trigger_evening_events(self, sio):
        for p in self.alive_list:
            if (
                (
                    isinstance(p.role, roles.Jailor)
                    or isinstance(p.role, roles.Kidnapper)
                    or isinstance(p.role, roles.Interrogator)
                )
                and not p.jailed
                and p.has_jailed_whom
            ):
                p.has_jailed_whom.jailed = True
                p.crimes["납치"] = True
        for p in self.alive_list:
            if not p.jailed:
                if isinstance(p.role, roles.Jailor) and p.has_jailed_whom:
                    sio.enter_room(p.sid, p.has_jailed_whom.jailID)
                    data = {
                        "type": "has_jailed_someone",
                    }
                    await self.emit_event(sio, data, p.sid)
                    data = {
                        "type": "jailed",
                    }
                    await self.emit_event(sio, data, p.has_jailed_whom.sid)
                elif isinstance(p.role, roles.Kidnapper) and p.has_jailed_whom:
                    data = {
                        "type": "has_jailed_someone",
                    }
                    await self.emit_event(sio, data, p.sid)
                    for maf in self.alive_list:
                        if isinstance(maf.role, roles.Mafia) and not maf.jailed:
                            sio.enter_room(maf.sid, p.has_jailed_whom.jailID)
                    data = {
                        "type": "jailed",
                    }
                    await self.emit_event(sio, data, p.has_jailed_whom.sid)
                elif isinstance(p.role, roles.Interrogator) and p.has_jailed_whom:
                    data = {
                        "type": "has_jailed_someone",
                    }
                    await self.emit_event(sio, data, p.sid)
                    for trd in self.alive_list:
                        if isinstance(trd.role, roles.Triad) and not trd.jailed:
                            sio.enter_room(trd.sid, p.has_jailed_whom.jailID)
                    data = {
                        "type": "jailed",
                    }
                    await self.emit_event(sio, data, p.has_jailed_whom.sid)

    async def trigger_night_events(self, sio):
        # 감옥 채팅 나가기
        for p1 in self.alive_list:
            for p2 in self.alive_list:
                if p1 is not p2:
                    sio.leave_room(p1, p2.jailID)

        # 생존자 방탄 착용
        for p in self.alive_list:
            if isinstance(p.role, roles.Survivor) and p.wear_vest_today:
                p.role.defense_level = 1
                data = {
                    "type": "wear_vest_confirmed",
                    "wear_vest": p.wear_vest_today,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 시민 방탄 착용
        for p in self.alive_list:
            if isinstance(p.role, roles.Citizen) and p.wear_vest_today:
                p.role.defense_level = 1
                data = {
                    "type": "wear_vest",
                }
                await self.emit_event(sio, data, room=p.sid)

        # 마녀 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Witch) and p.target1 and p.target2:
                p.target1.visited_by[self.day].add(p)
                if (isinstance(p.target1, roles.Veteran) and p.target1.alert_today) or (
                    isinstance(p.target1, roles.MassMurderer) and p.target1.murder_today
                ):
                    continue
                else:
                    p.target1.target1 = p.target2
                    p.target1.controlled_by = p
                    data = {
                        "type": "Witch_control_success",
                        "target1": p.target1.nickname,
                        "target2": p.target2.nickname,
                    }
                    await self.emit_event(sio, data, room=p.sid)
                    data = {
                        "type": "controlled_by_Witch",
                    }
                    await self.emit_event(sio, data, room=p.target1.sid)

        # 기생 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Escort) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.target1 = None
                p.target1.recruit_target = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {"type": "blocked"}
                await self.emit_event(sio, data, room=p.target1.sid)
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Town):
                    p.crimes["치안을 어지럽힘"] = True

        # 매춘부 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Consort) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.target1 = None
                p.target1.recruit_target = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {"type": "blocked"}
                await self.emit_event(sio, data, room=p.target1.sid)
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Town):
                    p.crimes["치안을 어지럽힘"] = True

        # 간통범 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Liaison) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.target1 = None
                p.target1.recruit_target = None
                p.target1.burn_today = False
                p.target1.curse_today = False
                data = {"type": "blocked"}
                await self.emit_event(sio, data, room=p.target1.sid)
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Town):
                    p.crimes["치안을 어지럽힘"] = True

        # 잠입자 능력 적용
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Beguiler)
                and p.target1
                and p.role.ability_opportunity > 0
            ):
                p.target1.visited_by[self.day].add(p)
                for p2 in self.alive_list:
                    if p2.target1 is p:
                        p2.target1 = p.target1
                        p2.controlled_by = p
                p.crimes["무단침입"] = True
                p.role.ability_opportunity -= 1
                # TODO: 자살유도 범죄 추가

        # 사기꾼 능력 적용
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Deceiver)
                and p.target1
                and p.role.ability_opportunity > 0
            ):
                p.target1.visited_by[self.day].add(p)
                for p2 in self.alive_list:
                    if p2.target1 is p:
                        p2.target1 = p.target1
                        p2.controlled_by = p
                p.crimes["무단침입"] = True
                p.role.ability_opportunity -= 1
                # TODO: 자살유도 범죄 추가

        # 방문자 모두 확정되면 방문자 목록에 추가
        # TODO: 방문자 로직 수정

        # 방화범 기름칠 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Arsonist) and not p.burn_today and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.oiled = True
                data = {
                    "type": "oiling_success",
                    "target1": p.target1.nickname,
                }
                await self.emit_event(sio, data, room=p.sid)
                p.crimes["무단침입"] = True

        # 의사 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Doctor) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.healed_by.append(p)

        # 경호원 능력 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Bodyguard) and p.target1:
                p.target1.visited_by[self.day].add(p)
                p.target1.bodyguarded_by.append(p)

        # 사망자 발생 시작
        # 경계 중인 퇴역군인에게 간 애들부터 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Veteran) and p.alert_today:
                p.crimes["재물 손괴"] = True
                for visitor in [visitor for visitor in self.alive_list if visitor.target1 is p]:
                    p.visited_by[self.day].add(visitor)
                    if isinstance(visitor.role, roles.Lookout):
                        continue
                    if isinstance(visitor.role, roles.Doctor) or isinstance(
                        visitor.role, roles.WitchDoctor
                    ):
                        p.healed_by.remove(visitor)
                    elif isinstance(visitor.role, roles.Bodyguard):
                        p.bodyguarded_by.remove(visitor)
                    data = {"type": "someone_visited_to_Veteran"}
                    await self.emit_event(sio, data, room=p.sid)
                    data = {
                        "type": "visited_Veteran",
                        "with_Bodyguard": len(visitor.bodyguarded_by) != 0,
                    }
                    await self.emit_event(sio, data, room=visitor.sid)
                    if self.killable(p, visitor):
                        if visitor.bodyguarded_by:
                            BG = visitor.bodyguarded_by.pop()  # BG stands for Bodyguard
                            await visitor.bodyguarded(room=self, attacker=p)
                            await self.emit_sound(sio, BG.role.name)
                            data = {
                                "type": "fighted_with_bodyguard",
                            }
                            await self.emit_event(sio, data, room=p.sid)
                            if BG.healed_by:
                                H = BG.healed_by.pop()
                                await BG.healed(room=self, attacker=p, healer=H)
                            else:
                                await BG.die(attacker=p, dead_while_guarding=True, room=self)
                                p.crimes["살인"] = True
                        elif visitor.healed_by:
                            H = visitor.healed_by.pop()
                            await self.emit_sound(sio, visitor.role.name)
                            await p.healed(room=self, attacker=p, healer=H)
                        else:
                            await self.emit_sound(sio, p.role.name)
                            await visitor.die(attacker=p, die_today=self.die_today, room=self)
                            p.crimes["살인"] = True
                    else:
                        await self.emit_sound(sio, p.role.name, dead=False)
                        await visitor.attacked(room=self, attacker=p)

        # 간수의 처형대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Jailor)
                and p.kill_the_jailed_today
                and p.role.ability_opportunity > 0
            ):
                await self.emit_sound(sio, roles.Jailor.name)
                await p.has_jailed_whom.die(attacker=p, room=self)
                p.crimes["살인"] = True
                p.role.ability_opportunity -= 1

        # 납치범의 처형대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Kidnapper)
                and p.kill_the_jailed_today
                and p.role.ability_opportunity > 0
            ):
                await self.emit_sound(sio, roles.Jailor.name)
                await p.has_jailed_whom.die(attacker=p, room=self)
                p.crimes["살인"] = True
                p.role.ability_opportunity -= 1

        # 심문자의 처형대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Interrogator)
                and p.kill_the_jailed_today
                and p.role.ability_opportunity > 0
            ):
                await self.emit_sound(sio, roles.Jailor.name)
                await p.has_jailed_whom.die(attacker=p, room=self)
                p.crimes["살인"] = True
                p.role.ability_opportunity -= 1
        # TODO: 조종자살 시 소리만 나는 것 수정
        # 자경대원의 대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Vigilante) and p.target1:
                victim = p.target1
                victim.visited_by[self.day].add(p)
                if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await p.suicide(room=self, reason=p.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=p.sid)
                    continue
                p.crimes["무단침입"] = True
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                    await victim.bodyguarded(room=self, attacker=p)
                    await self.emit_sound(sio, BG.role.name)
                    if p.healed_by:
                        H = p.healed_by.pop()  # H stands for Healer
                        await p.healed(room=self, attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif self.killable(p, victim):
                    await self.emit_sound(sio, p.role.name)
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await victim.healed(room=self, attacker=p, healer=H)
                    else:
                        await victim.die(attacker=p, room=self)
                        p.crimes["살인"] = True
                else:
                    await self.emit_sound(sio, p.role.name, dead=False)
                    await victim.attacked(room=self, attacker=p)

        # 마피아의 대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Mafioso) or isinstance(p.role, roles.Godfather)
            ) and p.target1:
                victim = p.target1
                victim.visited_by[self.day].add(p)
                if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await p.suicide(room=self, reason=p.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=p.sid)
                    continue
                p.crimes["무단침입"] = True
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                    await victim.bodyguarded(room=self, attacker=p)
                    await self.emit_sound(sio, BG.role.name)
                    if p.healed_by:
                        H = p.healed_by.pop()  # H stands for Healer
                        await p.healed(room=self, attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif self.killable(p, victim):
                    await self.emit_sound(sio, roles.Mafioso.name)
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await victim.healed(room=self, attacker=p, healer=H)
                    else:
                        await victim.die(attacker=p, room=self)
                        p.crimes["살인"] = True
                else:
                    await self.emit_sound(sio, roles.Mafioso.name, dead=False)
                    await victim.attacked(room=self, attacker=p)

        # 삼합회의 대상이 죽는다.
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.Enforcer)
                or isinstance(p.role, roles.DragonHead)
            ) and p.target1:
                victim = p.target1
                victim.visited_by[self.day].add(p)
                if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await p.suicide(room=self, reason=p.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=p.sid)
                    continue
                p.crimes["무단침입"] = True
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                    await victim.bodyguarded(room=self, attacker=p)
                    await self.emit_sound(sio, BG.role.name)
                    if p.healed_by:
                        H = p.healed_by.pop()  # H stands for Healer
                        await p.healed(room=self, attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif self.killable(p, victim):
                    await self.emit_sound(sio, roles.Mafioso.name)
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await victim.healed(room=self, attacker=p, healer=H)
                    else:
                        await victim.die(attacker=p, room=self)
                        p.crimes["살인"] = True
                else:
                    await self.emit_sound(sio, roles.Mafioso.name, dead=False)
                    await victim.attacked(room=self, attacker=p)

        # 연쇄살인마의 대상이 죽는다.
        for p in self.alive_list:
            if isinstance(p.role, roles.SerialKiller) and p.target1:
                victim = p.target1
                victim.visited_by[self.day].add(p)
                if isinstance(victim.role, roles.Veteran) and victim.alert_today:
                    continue
                if victim == p:
                    if self.killable(p, p):
                        await self.emit_sound(sio, "Suicide_by_control")
                        await p.suicide(room=self, reason=p.controlled_by.role.name)
                    else:
                        data = {"type": "almost_suicide"}
                        await self.emit_event(sio, data, room=p.sid)
                    continue
                p.crimes["무단침입"] = True
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()  # BG stands for Bodyguard
                    await victim.bodyguarded(room=self, attacker=p)
                    await self.emit_sound(sio, BG.role.name)
                    if p.healed_by:
                        H = p.healed_by.pop()  # H stands for Healer
                        await p.healed(room=self, attacker=p, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p, healer=H, dead_while_guarding=True)
                    else:
                        await BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif self.killable(p, victim):
                    await self.emit_sound(sio, p.role.name)
                    if victim.healed_by:
                        H = victim.healed_by.pop()
                        await victim.healed(room=self, attacker=p, healer=H)
                    else:
                        await victim.die(attacker=p, room=self)
                        p.crimes["살인"] = True
                else:
                    await self.emit_sound(sio, p.role.name, dead=False)
                    await victim.attacked(room=self, attacker=p)

        # 방화범이 불을 피운다.
        for p in self.alive_list:
            if isinstance(p.role, roles.Arsonist) and p.burn_today:
                p.crimes["방화"] = True
                p.crimes["재물 손괴"] = True
                victims = {v for v in self.alive_list if v.oiled}
                for v in victims:
                    if v.target1:
                        victims.add(v.target1)
                await self.emit_sound(sio, p.role.name, number_of_murdered=len(victims))
                for victim in self.victims:
                    if self.killable(p, victim):
                        if victim.healed_by:
                            H = victim.healed_by.pop()
                            victim.healed(room=self, attacker=p, healer=H)
                        else:
                            victim.die(attacker=p, room=self)
                            p.crimes["살인"] = True
                    else:
                        victim.attacked(room=self, attacker=p)

        # 비밀조합장의 살인 적용
        for p in self.alive_list:
            if (
                isinstance(p.role, roles.MasonLeader)
                and p.target1
                and isinstance(p.target1.role, roles.Cult)
            ):
                p.crimes["호객행위"] = True
                p.crimes["무단침입"] = True
                victim = p.target1
                victim.visited_by[self.day].add(p)
                data = {
                    "type": "visited_cult",
                }
                await self.emit_event(sio, data, room=p.sid)
                if victim.bodyguarded_by:
                    BG = victim.bodyguarded_by.pop()
                    await self.emit_sound(sio, BG.role.name)
                    await victim.bodyguarded(room=self, attacker=p)
                    if p.healed_by:
                        H = p.healed_by.pop()
                        await p.healed(room=self, attacker=BG, healer=H)
                    else:
                        await p.die(attacker=BG, room=self)
                        BG.crimes["살인"] = True
                    if BG.healed_by:
                        H = BG.healed_by.pop()
                        await BG.healed(room=self, attacker=p)
                    else:
                        BG.die(attacker=p, dead_while_guarding=True, room=self)
                        p.crimes["살인"] = True
                elif not self.killable(p, victim):
                    await self.emit_sound(sio, p.role.name)
                    await victim.attacked(room=self, attacker=p)
                elif victim.healed_by:
                    H = victim.healed_by.pop()
                    await self.emit_sound(sio, p.role.name)
                    await victim.healed(room=self, attacker=p, healer=H)
                else:
                    await self.emit_sound(sio, p.role.name)
                    await victim.die(attacker=p, room=self)
                    p.crimes["살인"] = True

        # 대량학살자 살인 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.MassMurderer) and p.target1:
                p.crimes["무단침입"] = True
                p.target1.visited_by[self.day].add(p)
                victims = {
                    v
                    for v in self.alive_list
                    if (
                        v.target1 is p.target1
                        or (isinstance(v.role, roles.Bodyguard) and v.target1 is p)
                    )
                    and v is not p
                }  # 경호원이 대학 경호 시 사망하는 것 구현
                if p.target1.target1 is None:
                    victims.add(p.target1)
                await self.emit_sound(sio, p.role.name, number_of_murdered=len(victims))
                if len(victims) > 1:
                    p.crimes["재물손괴"] = True
                for v in victims:
                    if v.bodyguarded_by:
                        BG = v.bodyguarded_by.pop()
                        await v.bodyguarded(room=self, attacker=p)
                        if p.healed_by:
                            H = p.healed_by.pop()
                            await p.healed(room=self, attacker=BG, healer=H)
                        else:
                            await p.die(attacker=BG, room=self)
                            BG.crimes["살인"] = True
                        if BG.healed_by:
                            H = BG.healed_by.pop()
                            await BG.healed(room=self, attacker=p, healer=H)
                        else:
                            await BG.die(attacker=p, room=self)
                            p.crimes["살인"] = True
                    elif not self.killable(p, v):
                        await v.attacked(room=self, attacker=p)
                    elif v.healed_by:
                        H = v.healed_by.pop()
                        await v.healed(room=self, attacker=p, healer=H)
                    else:
                        await v.die(attacker=p, room=self)
                        p.crimes["살인"] = True

        # 어릿광대 자살 적용
        candidates = [p for p in self.alive_list if p.voted_to_execution_of_jester]
        random.shuffle(candidates)
        if candidates:
            victim = candidates.pop()
            await self.emit_sound(sio, "자살")
            if victim.healed_by:
                H = victim.healed_by.pop()
                class Dummy:
                    pass
                d = Dummy()
                d.role = Dummy()
                d.role.name = roles.Jester.name
                await victim.healed(room=self, attacker=d, healer=H)
            else:
                await victim.suicide(room=self, reason=roles.Jester.name)

        # TODO: 심장마비 자살
        # TODO: 변장자
        # TODO: 밀고자

        # 고의 자살 적용

        # 마녀 저주 적용
        for p in self.alive_list:
            if isinstance(p.role, roles.Witch) and p.curse_target and not p.has_cursed:
                victim = p.curse_target
                if victim.healed_by:
                    H = victim.healed_by.pop()
                    await victim.healed(room=self, attacker=p, healer=H)
                else:
                    await victim.die(attacker=p, room=self)

        # 사망자들 제거
        for dead in self.die_today:
            self.alive_list.remove(dead)

        # 살인직들의 살인이 반영된 방문자 목록 갱신
        for p in self.alive_list:
            if p.target1:
                p.target1.visited_by[self.day].add(p)
        # TODO: 변장자, 밀고자 (사망자들 제거된 이후에 능력 발동됨)
        # TODO: 관리인/향주 직업 수거
        # TODO: 조작자/위조꾼

        # 고의 자살 적용
        for p in self.alive_list:
            if p.suicide_today:
                await self.emit_sound(sio, "자살")
                if p.healed_by:
                    H = p.healed_by.pop()
                    class Dummy:  # dummy class
                        pass
                    dummy = Dummy()
                    dummy.role = Dummy()
                    dummy.role.name = "자살"
                    await p.healed(room=self, attacker=dummy, healer=H)
                else:
                    await p.suicide(room=self, reason="고의")
                    self.die_today.add(p)
                    self.alive_list.remove(p)
        # 조사직들 능력 발동
        # 검시관
        for p in self.alive_list:
            if isinstance(p.role, roles.Coroner) and p.target1 and not p.target1.alive:
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": [[(visitor.nickname, visitor.role) for visitor in visitors] for visitors in p.target1.visited_by[1:]]
                }
                await self.emit_event(sio, data, room=p.sid)

        # 형사
        for p in self.alive_list:
            if isinstance(p.role, roles.Detective) and p.target1:
                p.crimes["무단침입"] = True
                result = None
                for visited in self.alive_list:
                    if p.target1 in visited.visited_by[self.day]:
                        # 그냥 p.taget1.target1을 주지 않고 이렇게 복잡하게 하는 것은
                        # p.target1이 자신의 target1만 설정해놓고 실제로 능력을 쓰지는 못하고 이날 밤에 죽었을 경우에(퇴군에게 죽었을 경우를 제외)
                        # None이 아닌 p.target1.target1을 주게 되면 형사 입장에서는 자기 목표가 능력을 쓰고 죽은 걸로 착각하게 되기 떄문이다.
                        # 예시: 탐정이 시장을 방문. 대부가 탐정을 방문. 형사가 탐정을 방문.
                        # 이때 그냥 p.target1.target1을 주게 되면 형사에게는 탐정이 시장을 방문한 것으로 보이게 됨. 실제로는 방문하지 못했음에도 불구.
                        # 따라서 각 플레이어들의 visited_by에 p.target1이 들어가 있는지를 확인하여 실제로 방문했을 때만 결과를 전송해야 한다.
                        result = visited.nickname
                        break
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": result,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 탐정
        for p in self.alive_list:
            if isinstance(p.role, roles.Investigator) and p.target1:
                p.crimes["무단침입"] = True
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": p.target1.crimes,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 감시자
        for p in self.alive_list:
            if isinstance(p.role, roles.Lookout) and p.target1:
                p.crimes["무단침입"] = True
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": [p.nickname for p in p.target1.visited_by[self.day]]
                }
                await self.emit_event(sio, data, room=p.sid)

        # 보안관
        for p in self.alive_list:
            if isinstance(p.role, roles.Sheriff) and p.target1:
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": None,
                }
                for evil in (roles.Mafia, roles.Triad, roles.Cult):
                    if isinstance(p.target1.role, evil):
                        data["result"] = evil.team
                        break
                else:
                    for killing in (roles.SerialKiller, roles.MassMurderer, roles.Arsonist):
                        if isinstance(p.target1.role, killing):
                            data["result"] = killing.name
                            break
                await self.emit_event(sio, data, room=p.sid)

        # 조언자
        for p in self.alive_list:
            if isinstance(p.role, roles.Consigliere) and p.target1:
                p.crimes["무단침입"] = True
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": p.target1.role.name,
                }
                await self.emit_event(sio, data, room=p.sid)

        # 백지선
        for p in self.alive_list:
            if isinstance(p.role, roles.Administrator) and p.target1:
                p.crimes["무단침입"] = True
                data = {
                    "type": "check_result",
                    "role": p.role.name,
                    "result": p.target1.role.name,
                }
                await self.emit_event(sio, data, room=p.sid)

        # TODO: 변장자 이동
        # 정보원
        for p in self.alive_list:
            if isinstance(p.role, roles.Spy):
                for p2 in self.alive_list:
                    if (isinstance(p2.role, roles.Mafia) or isinstance(p2.role, roles.Triad)) and p2.target1:
                        data = {
                            "type": "spy_result",
                            "team": p2.role.team,
                            "result": p2.target1.nickname,
                        }
                        await self.emit_event(sio, data, room=p.sid)
        # TODO: 어릿광대 괴롭히기
        # 회계
        for p in self.alive_list:
            if isinstance(p.role, roles.Auditor) and p.target1:
                if p.target1.role.defense_level > 0 or isinstance(
                    p.target1.role, roles.Cult
                ):
                    data = {
                        "type": "unable_to_audit",
                    }
                    await self.emit_event(sio, data, room=p.sid)
                else:
                    if p.target1 is p:
                        await self.convert_role(
                            sio, convertor=p, converted=p, role=roles.Stump()
                        )
                    elif isinstance(p.target1.role, roles.Mafia):
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Mafioso()
                        )
                    elif isinstance(p.target1.role, roles.Triad):
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Triad()
                        )
                    elif isinstance(p.target1.role, roles.Town):
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Citizen()
                        )
                    else:
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Scumbag()
                        )
                    data = {
                        "type": "audit_success",
                        "role": p.target1.role.name,
                        "who": p.target1.nickname,
                    }
                    await self.emit_event(sio, data, room=p.sid)
                    p.crimes["부패"] = True

        # 비밀조합 영입
        for p in self.alive_list:
            if isinstance(p.role, roles.MasonLeader) and p.target1:
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Citizen):
                    await self.convert_role(
                        sio, convertor=p, converted=p.target1, role=roles.Mason()
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.target1.role.name,
                        "who": p.target1.nickname,
                    }
                    await self.emit_event(sio, data, room=p.sid)
                elif not isinstance(p.target1.role, roles.Cult):
                    data = {"type": "recruit_failed"}
                    await self.emit_event(sio, data, room=p.sid)

        # 이교도 개종
        for p in self.alive_list:
            if isinstance(p.role, roles.Cultist) and p.target1:
                p.crimes["호객행위"] = True
                if isinstance(p.target1.role, roles.Mason) or isinstance(
                    p.target1.role, roles.MasonLeader
                ):
                    data = {
                        "type": "recruited_by_cult",
                        "who": p.nickname,
                    }
                    await self.emit_event(sio, data, room=p.target1.sid)
                    data = {"type": "tried_to_recruit_Mason", "who": p.target1.nickname}
                    await self.emit_event(sio, data, room=self.cultChatID)
                elif p.target1.role.defense_level > 0:
                    data = {
                        "type": "recruit_failed",
                    }
                    await self.emit_event(sio, data, room=self.cultChatID)
                elif isinstance(p.target1.role, roles.Mafia) or isinstance(
                    p.target1.role, roles.Triad
                ):
                    data = {
                        "type": "recruited_by_cult",
                        "who": p.nickname,
                    }
                    await self.emit_event(sio, data, room=p.target1.sid)
                    data = {
                        "type": "recruit_failed",
                    }
                    await self.emit_event(sio, data, room=self.cultChatID)
                else:
                    if (
                        isinstance(p.target1.role, roles.Witch)
                        or isinstance(p.target1.role, roles.Doctor)
                        and roles.WitchDoctor.name
                        not in {p.role.name for p in self.players}
                    ):
                        await self.convert_role(
                            sio,
                            convertor=p,
                            converted=p.target1,
                            role=roles.WitchDoctor(),
                        )
                    else:
                        await self.convert_role(
                            sio, convertor=p, converted=p.target1, role=roles.Cultist()
                        )
                    data = {
                        "type": "recruit_success",
                        "role": p.target1.role.name,
                        "who": p.target1.nickname,
                    }
                    await self.emit_event(sio, data, room=self.cultChatID)
                    p.crimes["음모"] = True

        # 마피아 영입
        for p in self.alive_list:
            if isinstance(p.role, roles.Godfather) and p.recruit_target:
                if isinstance(p.recruit_target.role, roles.Citizen):
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Mafioso(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.mafiaChatID)
                elif isinstance(p.recruit_target.role, roles.Escort):
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Consort(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.mafiaChatID)
                else:
                    data = {"type": "recruit_failed"}
                    await self.emit_event(sio, data, room=self.mafiaChatID)

        # 삼합회 영입
        for p in self.alive_list:
            if isinstance(p.role, roles.DragonHead) and p.recruit_target:
                if isinstance(p.recruit_target.role, roles.Citizen):
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Enforcer(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.triadChatID)
                elif isinstance(p.recruit_target.role, roles.Escort):
                    await self.convert_role(
                        sio,
                        convertor=p,
                        converted=p.recruit_target,
                        role=roles.Liaison(),
                    )
                    data = {
                        "type": "recruit_success",
                        "role": p.recruit_target.role.name,
                        "who": p.recruit_target.nickname,
                    }
                    await self.emit_event(sio, data, room=self.triadChatID)
                else:
                    data = {"type": "recruit_failed"}
                    await self.emit_event(sio, data, room=self.triadChatID)

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
            p.jailed_by = []
            p.has_jailed_whom = None
            p.bodyguarded_by = []
            p.healed_by = []
            p.target1 = None
            p.target2 = None
            p.curse_target = None
            p.recruit_target = None

    def game_over(self):
        remaining = self.alive_list
        if len(remaining) == 0 or len(remaining) == 1 or len(remaining) == 2:
            return True
        townRemains = False
        mafiaRemains = False
        triadRemains = False
        neutralKillingRemains = False
        neutralEvilThatIsNotNeutralKillingRemains = False
        for p in remaining:
            if isinstance(p.role, roles.Town):
                townRemains = True
            elif isinstance(p.role, roles.Mafia):
                mafiaRemains = True
            elif isinstance(p.role, roles.Triad):
                triadRemains = True
            elif isinstance(p.role, roles.NeutralKilling):
                neutralKillingRemains = True
            elif isinstance(p.role, roles.NeutralEvil) and not isinstance(
                p.role, roles.NeutralKilling
            ):
                neutralEvilThatIsNotNeutralKillingRemains = True
        if townRemains:
            return (
                not mafiaRemains
                and not triadRemains
                and not neutralKillingRemains
                and not neutralEvilThatIsNotNeutralKillingRemains
            )
        if mafiaRemains:
            return not triadRemains and not neutralKillingRemains
        if triadRemains:
            return not neutralKillingRemains
        if neutralKillingRemains:  # 중살들밖에 안남은 경우
            arsonistRemains = False
            massMurdererRemains = False
            serialKillerRemains = False
            for p in remaining:
                if isinstance(p.role, roles.Arsonist):
                    arsonistRemains = True
                elif isinstance(p.role, roles.MassMurderer):
                    massMurdererRemains = True
                elif isinstance(p.role, roles.SerialKiller):
                    serialKillerRemains = True
            return not (arsonistRemains and massMurdererRemains and serialKillerRemains)
        return True  # 중선들만 남은 경우

    def win(self, winning_role, include_dead):
        if include_dead:
            for p in self.players.values():
                if isinstance(p.role, winning_role):
                    p.win = True
        else:
            for p in self.alive_list:
                if isinstance(p.role, winning_role):
                    p.win = True

    async def init_game(self, sio):
        # init game
        print("Game initiated in room #", self.roomID)
        self.inGame = True
        self.election = asyncio.Event()
        self.day = 0
        self.die_today = set()
        self.message_record = [] # 초기화
        if self.setup=="test":
            self.STATE = "MORNING"  # game's first state when game starts
            self.MORNING_TIME = 5
            self.DISCUSSION_TIME = 10
            self.VOTE_TIME = 10
            self.DEFENSE_TIME = 10
            self.VOTE_EXECUTION_TIME = 10
            self.EVENING_TIME = 10
        if self.setup == "8331":
            pass
        elif self.setup == "power_conflict":
            pass
        elif self.setup == "test":
            roles_to_distribute = [
                roles.DragonHead(),
                roles.Beguiler(),
                roles.Mafioso(),
                roles.Spy(),
                roles.Witch(),
            ]
        # random.shuffle(roles_to_distribute)
        self.players = {
            (await sio.get_session(sid))["nickname"]: Player(
                sid=sid,
                roomID=self.roomID,
                nickname=(await sio.get_session(sid))["nickname"],
                role=roles_to_distribute.pop(),
                sio=sio,
            )
            for sid in self.members
        }

        for p in self.players.values():
            if isinstance(p.role, roles.Spy):
                p.crimes["무단침입"] = True

        self.hellID = str(self.roomID) + "_hell"
        self.mafiaChatID = str(self.roomID) + "_Mafia"
        self.triadChatID = str(self.roomID) + "_Triad"
        self.cultChatID = str(self.roomID) + "_Cult"
        self.spyRoomID = str(self.roomID) + "_Spy"
        self.masonChatID = str(self.roomID) + "_Mason"

        for p in self.players.values():
            sio.enter_room(p.sid, p.jailID)
            if isinstance(p.role, roles.Mafia):
                sio.enter_room(p.sid, self.mafiaChatID)
                p.nightChatID = self.mafiaChatID
            elif isinstance(p.role, roles.Triad):
                sio.enter_room(p.sid, self.triadChatID)
                p.nightChatID = self.triadChatID
            elif isinstance(p.role, roles.Cult):
                sio.enter_room(p.sid, self.cultChatID)
                p.nightChatID = self.cultChatID
            elif isinstance(p.role, roles.Spy):
                sio.enter_room(p.sid, self.spyRoomID)
                p.nightChatID = self.spyRoomID
            elif isinstance(p.role, roles.Mason) or isinstance(
                p.role, roles.MasonLeader
            ):
                sio.enter_room(p.sid, self.masonChatID)
                p.nightChatID = self.masonChatID

        self.alive_list = list(self.players.values())
        await asyncio.gather(*[self.emit_event(sio, {"type": "role", "role": p.role.name}, room=p.sid) for p in self.players.values()])

    async def run_game(self, sio):
        print("Game starts in room #", self.roomID)
        while True:
            self.day += 1
            # MORNING
            self.STATE = "MORNING"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            for dead in self.die_today:
                data = {
                    "type": "dead_announce",
                    "dead": dead.nickname,
                    "lw": dead.lw,
                }
                await self.emit_event(sio, data, room=self.roomID)
                await asyncio.sleep(5)
            if self.game_over():
                return
            self.die_today = set() # 사망자 목록 초기화
            # DISCUSSION
            self.STATE = "DISCUSSION"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await asyncio.sleep(self.DISCUSSION_TIME)
            # VOTE
            self.STATE = "VOTE"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            self.VOTE_ENDS_AT = datetime.now() + timedelta(seconds=self.VOTE_TIME)
            self.VOTE_TIME_REMAINING = (
                self.VOTE_ENDS_AT - datetime.now()
            ).total_seconds()
            while self.VOTE_TIME_REMAINING >= 0:
                try:
                    await asyncio.wait_for(
                        self.election.wait(), timeout=self.VOTE_TIME_REMAINING
                    )
                except asyncio.TimeoutError:  # nobody has been elected today
                    break
                else:  # someone has been elected
                    self.STATE = "DEFENSE"
                    data = {
                        "type": "state",
                        "state": self.STATE,
                        "who": self.elected.nickname,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    await asyncio.sleep(self.DEFENSE_TIME)
                    self.STATE = "VOTE_EXECUTION"
                    data = {
                        "type": "state",
                        "state": self.STATE,
                        "who": self.elected.nickname,
                    }
                    await self.emit_event(sio, data, room=self.roomID)
                    await asyncio.sleep(self.VOTE_EXECUTION_TIME)
                    if self.elected.voted_guilty > self.elected.voted_innocent:
                        await self.elected.die(attacker="VOTE", room=self)
                        break
                    else:
                        self.VOTE_TIME_REMAINING = (
                            self.VOTE_ENDS_AT - datetime.now()
                        ).total_seconds()
                        self.STATE = "VOTE"
                        data = {
                            "type": "state",
                            "state": self.STATE,
                        }
                        await self.emit_event(sio, data, room=self.roomID)
                finally:
                    self.election.clear()
                    self.elected = None

            if self.game_over():
                return
            # EVENING
            self.STATE = "EVENING"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await self.trigger_evening_events(sio)
            await asyncio.sleep(self.EVENING_TIME)

            # NIGHT
            self.STATE = "NIGHT"
            data = {
                "type": "state",
                "state": self.STATE,
            }
            await self.emit_event(sio, data, room=self.roomID)
            await self.trigger_night_events(sio)
            await self.clear_up()

    async def finish_game(self, sio):
        print("Game finished in room #", self.roomID)
        remaining = self.alive_list
        if len(remaining) == 0:
            pass
        else:
            # 같이 이길 수 없는 세력들
            for p in remaining:
                if isinstance(p.role, roles.Arsonist):
                    self.win(roles.Arsonist, False)
                    break
            else:
                for p in remaining:
                    if isinstance(p.role, roles.SerialKiller):
                        self.win(roles.SerialKiller, False)
                        break
                else:
                    for p in remaining:
                        if isinstance(p.role, roles.MassMurderer):
                            self.win(roles.MassMurderer, False)
                            break
                    else:
                        for p in remaining:
                            if isinstance(p.role, roles.Triad):
                                self.win(roles.Triad, True)
                                break
                        else:
                            for p in remaining:
                                if isinstance(p.role, roles.Mafia):
                                    self.win(roles.Mafia, True)
                                    break
                            else:
                                for p in remaining:
                                    if isinstance(p.role, roles.Cult):
                                        self.win(roles.Cult, True)
                                        break
                                else:
                                    for p in remaining:
                                        if isinstance(p.role, roles.NeutralEvil):
                                            self.win(roles.NeutralEvil, False)
                                            break
                                    else:
                                        for p in remaining:
                                            if isinstance(p.role, roles.Town):
                                                self.win(roles.Town, True)
                                                break
            for p in remaining:
                if isinstance(p.role, roles.Scumbag):
                    self.win(roles.Scumbag, False)
                elif isinstance(p.role, roles.Witch):
                    self.win(roles.Witch, False)
                elif isinstance(p.role, roles.Judge):
                    self.win(roles.Judge, False)
                elif isinstance(p.role, roles.Auditor):
                    self.win(roles.Auditor, False)
                elif isinstance(p.role, roles.Survivor):
                    self.win(roles.Survivor, False)
                elif isinstance(p.role, roles.Amnesiac):
                    self.win(roles.Amnesiac, False)
        data = {
            "type": "game_over",
            "winner": [p.nickname for p in self.players.values() if p.win]
        }
        await self.emit_event(sio, data, room=self.roomID)
        self.inGame = False
        for in_game_chatID in (self.hellID,
                               self.mafiaChatID,
                               self.triadChatID,
                               self.cultChatID,
                               self.spyRoomID,
                               self.masonChatID):
            await sio.close_room(in_game_chatID)
        for p in self.players.values():
            await sio.close_room(p.jailID)
        async with aiosqlite.connect("sql/records.db") as DB:
            def get_random_alphanumeric_string(length): # TODO: 정말로 alphanum만 오는지 확인 (SQL 인젝션 방어)
                letters_and_digits = string.ascii_letters + string.digits
                result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
                return result_str
            async def insert(DB, record):
                query = f'INSERT INTO {gamelog_id} values ({record[0]}, "{record[1]}", "{record[2]}");'
                await DB.execute(query)
                await DB.commit()
            while True:
                try:
                    gamelog_id = get_random_alphanumeric_string(16)
                    query = f"CREATE TABLE {gamelog_id} (time real not null, message string not null, receivers string not null);"
                    await DB.execute(query)
                    break
                except sqlite3.OperationalError:
                    continue
            await asyncio.gather(*[insert(DB, record) for record in self.message_record])
            data = {
                "type": "save_done",
                "link": gamelog_id, # TODO: link to the archive
            }
            await sio.emit("event", data, room=self.roomID)
        del self.alive_list
        del self.players
        del self

    async def someone_entered(self, sid, sio):
        player_list = list(map(lambda s: s["nickname"], await asyncio.gather(*[sio.get_session(sid) for sid in self.members])))
        await sio.emit("player_list", player_list, room=self.roomID)
        if self.inGame:
            enterer = (await sio.get_session(sid))["nickname"]
            if enterer in self.players and self.players[enterer].alive:
                pass
            else:
                sio.enter_room(sid, self.hellID)

    async def someone_left(self, sid, sio):
        player_list = list(map(lambda s: s["nickname"], await asyncio.gather(*[sio.get_session(sid) for sid in self.members])))
        await sio.emit("player_list", player_list, room=self.roomID)
        if self.inGame:
            for p in self.players.values():
                if p.sid==sid:
                    p.suicide_today = True
                    break


class Player:
    def __init__(self, sid, roomID, nickname, role, sio, alive=True):
        self.sid = sid
        self.nickname = nickname
        self.role = role
        self.role_record = [self.role]
        self.sio = sio
        self.alive = alive
        self.win = False
        self.votes = 1
        self.has_voted = False
        self.voted_to_whom = None
        self.voted_to_execution_of_jester = False
        self.has_voted_in_execution_vote = False
        self.voted_to_which = None
        self.votes_gotten = 0
        self.voted_guilty = 0
        self.voted_innocent = 0
        self.lw = ""  # last will
        self.visited_by = [None, set()]
        self.controlled_by = None
        self.wear_vest_today = False
        self.alert_today = False
        self.burn_today = False
        self.curse_today = False
        self.suicide_today = False
        self.cannot_murder_until = 0
        self.protected_from_cult = False
        self.protected_from_auditor = False
        self.oiled = False
        self.jailed = False
        self.jailed_by = []
        self.jailID = str(roomID) + "_Jail_" + self.nickname
        self.has_jailed_whom = None
        self.kill_the_jailed_today = False
        self.has_disguised = False
        self.has_cursed = False
        self.bodyguarded_by = []  # list of Player objects
        self.healed_by = []  # list of Player objects
        self.target1 = None
        self.target2 = None
        self.curse_target = None
        self.recruit_target = None
        self.nightChatID = None
        self.crimes = {
            "무단침입": False,
            "납치": False,
            "부패": False,
            "신분도용": False,
            "호객행위": False,
            "살인": False,
            "치안을 어지럽힘": False,
            "음모": False,
            "재물 손괴": False,
            "방화": False,
        }

    async def die(self, room, attacker, dead_while_guarding=False):
        if attacker!="VOTE":
            room.die_today.add(self)
        self.alive = False
        data = {
            "type": "dead",
            "attacker": attacker.role.name if attacker!="VOTE" else "VOTE",
            "dead_while_guarding": dead_while_guarding,
        }
        await room.emit_event(self.sio, data, room=self.sid)
        if self.nightChatID:
            self.sio.leave_room(self.sid, self.nightChatID)
            self.nightChatID = None
        self.sio.enter_room(self.sid, room.hellID)

    async def attacked(self, room, attacker):
        data = {
            "type": "attacked",
            "attacker": attacker.role.name,
        }
        await room.emit_event(self.sio, data, room=self.sid)
        data = {
            "type": "attack_failed",
        }
        await room.emit_event(self.sio, data, room=attacker.sid)

    async def healed(self, room, attacker, healer):
        data = {
            "type": "healed",
            "attacker": attacker.role.name,
            "healer": healer.role.name,
        }
        await room.emit_event(self.sio, data, room=self.sid)

    async def bodyguarded(self, room, attacker):
        data = {
            "type": "bodyguarded",
            "attacker": attacker.role.name,
        }
        await room.emit_event(self.sio, data, room=self.sid)

    async def suicide(self, room, reason):
        # TODO: suicide(room=self, )를 그냥 die()로 대체
        data = {
            "type": "suicide",
            "reason": reason,
        }
        await room.emit_event(self.sio, data, room=self.sid)
