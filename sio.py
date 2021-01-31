import asyncio
import socketio
import json
from aioredis import create_redis_pool
from sanic.log import logger
from ast import literal_eval
from datetime import datetime

import game
from game.game import GameRoom


sio = socketio.AsyncServer(
    async_mode="sanic", cors_allowed_origins=["http://sc2mafia.kr", "http://localhost:8000"]
)

room_list = {}
next_roomID = 1

online_users = dict()


def setup_socketio(app):
    sio.attach(app)


@sio.event
async def connect(sid, environ):
    try:
        # KeyError occurs here
        HTTP_SID = environ["sanic.request"].cookies["session"]
        redis = await create_redis_pool("redis://localhost")
        HTTPsession = await redis.get("session:" + HTTP_SID)
        redis.close()
        await redis.wait_closed()
    except KeyError:  # occurs when request has no cookie named 'session'
        HTTPsession = None

    if HTTPsession is None:
        raise ConnectionRefusedError("인증필요")
    HTTPsession = HTTPsession.decode("ascii")
    HTTPsession = HTTPsession.replace("true", "True")
    HTTPsession = literal_eval(HTTPsession)
    if not HTTPsession.get("logged_in"):
        raise ConnectionRefusedError("인증필요")
    await sio.save_session(sid, HTTPsession)
    async with sio.session(sid) as user:
        if user['nickname'] in online_users:
            await sio.emit("multiple_login", {}, room=online_users[user["nickname"]])
            await sio.disconnect(online_users[user["nickname"]])
            online_users[user["nickname"]]=sid
        online_users[user["nickname"]]=sid
        logger.info("user connected: "+user["nickname"])


@sio.event
async def disconnect(sid):
    async with sio.session(sid) as user:
        nickname = user.get('nickname')
        if nickname is not None:
            logger.info("user disconnected: "+nickname)
            del online_users[nickname]
            if 'room' in user:
                await leave_GameRoom(sid, None)


@sio.event
async def enter_GameRoom(sid, data):
    assert "roomID" in data
    async with sio.session(sid) as user:
        if "room" in user:
            await leave_GameRoom(sid, None)
        roomID = data["roomID"]
        if roomID in room_list:
            if room_list[roomID].is_full():
                await sio.emit(
                    "failed_to_enter_GameRoom",
                    {
                        "reason": "full",
                    },
                    room=sid,
                )
            else:
                sio.enter_room(sid, roomID)
                user["room"] = roomID
                room = room_list[roomID]
                room.members.append(sid)
                if room.justCreated and user['nickname'] == room.host['nickname']:
                    room.host = sid
                    room.justCreated = False
                await sio.save_session(sid, user)
                await sio.emit('enter_GameRoom_success', roomID, room=sid)
                await sio.emit('event',
                               {'type': 'enter',
                                'who': user['nickname']},
                               room=roomID)
                await broadcast_room_list()
                await room.someone_entered(sid, sio)
        else:
            await sio.emit('failed_to_enter_GameRoom', {
                'reason': 'No such room',
            }, room=sid)


@sio.event
async def leave_GameRoom(sid, data):
    async with sio.session(sid) as user:
        assert "room" in user
        roomID = user["room"]
        room = room_list[roomID]
        room.members.remove(sid)
        sio.leave_room(sid, roomID)
        del user["room"]
        await sio.save_session(sid, user)
        await room.someone_left(sid, sio)
        if sid == room.host and room.members:
            room.host = room.members[0]
            data = {
                "type": "newhost",
                "who": (await sio.get_session(room.host))["nickname"],
            }
            await room.emit_event(sio, data, roomID)
        if not room.members:
            await sio.close_room(roomID)
            del room_list[roomID]
        await broadcast_room_list()
        await sio.emit(
            "event",
            {
                "type": "leave",
                "who": user["nickname"],
            },
            room=roomID,
        )
        await sio.emit("leave_GameRoom_success", {}, room=sid)


@sio.event
async def create_GameRoom(sid, data):
    # TODO: password
    global next_roomID
    assert type(data) is dict
    assert "title" in data
    assert "capacity" in data
    async with sio.session(sid) as user:
        room_list[next_roomID] = GameRoom(roomID=next_roomID,
                                          title=data['title'],
                                          capacity=data['capacity'],
                                          host=user,
                                          setup=data['setup'])
        await sio.emit('create_GameRoom_success', next_roomID, room=sid)
        next_roomID += 1
        await enter_GameRoom(sid, {"roomID": next_roomID-1})


@sio.event
async def kick(sid, kicked):
    if not isinstance(kicked, str): return
    async with sio.session(sid) as user:
        roomID = user.get("room")
        room = room_list.get(roomID)
        if not room or room.host!=sid: return
        if room.inGame:
            data = {
                "type": "unable_to_kick",
                "reason": "게임 중에는 강퇴할 수 없습니다."
            }
            await room.emit_event(sio, data, sid)
            return
        for m_sid in room.members:
            if (await sio.get_session(m_sid))["nickname"] == kicked:
                kicked_sid = m_sid
                break
        else:
            return
        data = {
            "type": "kick",
            "kicker": user["nickname"],
            "kicked": kicked,
        }
        await room.emit_event(sio, data, room.roomID)
        data = {
            "type": "kicked",
        }
        await room.emit_event(sio, data, kicked_sid)
        await leave_GameRoom(kicked_sid, None)


async def broadcast_room_list():
    to_send = {roomID: room.title for roomID, room in room_list.items()}
    await sio.emit("room_list", to_send)


@sio.event
async def request_room_list(sid, data):
    to_send = {roomID: room.title for roomID, room in room_list.items()}
    await sio.emit("room_list", to_send, room=sid)


@sio.event
async def message(sid, msg):
    if not isinstance(msg, str): return
    async with sio.session(sid) as user:
        logger.info(datetime.now().strftime("[%y/%m/%d %H:%M:%S] ")+user["nickname"]+": "+msg)
        if msg.startswith("/강퇴") and len(msg.split())>=2:
            await kick(sid, msg.split()[1])
        else:
            await room_list[user["room"]].handle_message(sio, sid, msg)
