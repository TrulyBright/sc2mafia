import asyncio
import game
import json
import socketio
import json
from aioredis import create_redis_pool
from ast import literal_eval

from game.game import GameRoom


sio = socketio.AsyncServer(
    async_mode="sanic", cors_allowed_origins="http://localhost:8080"
)

room_list = {}
next_roomID = 1

online_users = set()


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
        if user["username"] in online_users:
            raise ConnectionRefusedError("다중접속")
        online_users.add(user["username"])
        print("user connected:", user["username"])


@sio.event
async def disconnect(sid):
    async with sio.session(sid) as user:
        username = user.get("username")
        if username is not None:
            print("user disconnected: ", user.get("username"))
            online_users.remove(username)
            if "room" in user:
                await leave_GameRoom(sid, None)


@sio.event
async def enter_GameRoom(sid, data):
    assert "roomID" in data
    async with sio.session(sid) as user:
        if "room" in user:
            leave_GameRoom(sid, None)
        roomID = data["roomID"]
        if roomID in room_list:
            if room_list[roomID].isFull():
                print(user["username"], "fails to enter room #", roomID)
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
                if room.justCreated and user["username"] == room.host["username"]:
                    room.host = sid
                    room.justCreated = False
                await sio.save_session(sid, user)
                await sio.emit("enter_GameRoom_success", roomID, room=sid)
                await sio.emit(
                    "event", {"type": "enter", "who": user["nickname"]}, room=roomID
                )
                print(user["username"], "enters room #", roomID)
                await broadcast_room_list()
        else:
            print(user["username"], "fails to enter room #", roomID)
            await sio.emit(
                "failed_to_enter_GameRoom",
                {
                    "reason": "No such room",
                },
                room=sid,
            )


@sio.event
async def leave_GameRoom(sid, data):
    async with sio.session(sid) as user:
        assert "room" in user
        roomID = user["room"]
        room = room_list[roomID]
        room.members.remove(sid)
        print(user["username"], "leaves room #", roomID)
        sio.leave_room(sid, roomID)
        del user["room"]
        await sio.save_session(sid, user)
        if sid == room.host and room.members:
            room.host = room.members[0]
            print(
                "room #",
                roomID,
                "new host to",
                (await sio.get_session(room.host))["nickname"],
            )
            await sio.emit(
                "event",
                {
                    "type": "newhost",
                    "who": (await sio.get_session(room.host))["nickname"],
                },
                room=roomID,
            )
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


@sio.event
async def create_GameRoom(sid, data):
    # TODO: password
    global next_roomID
    assert type(data) is dict
    assert "title" in data
    assert "capacity" in data
    async with sio.session(sid) as user:
        print(user["username"], "creates room #", next_roomID)
        room_list[next_roomID] = GameRoom(
            roomID=next_roomID,
            title=data["title"],
            capacity=data["capacity"],
            host=user,
            setup=data["setup"],
        )
        await sio.emit("create_GameRoom_success", next_roomID, room=sid)
        next_roomID += 1
        await broadcast_room_list()


async def broadcast_room_list():
    to_send = {roomID: room.title for roomID, room in room_list.items()}
    await sio.emit("room_list", to_send)


@sio.event
async def request_room_list(sid, data):
    to_send = {roomID: room.title for roomID, room in room_list.items()}
    await sio.emit("room_list", to_send, room=sid)


@sio.event
async def message(sid, msg):
    assert type(msg) == str
    async with sio.session(sid) as user:
        await room_list[user["room"]].handle_message(sio, sid, msg)
