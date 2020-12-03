import asyncio
import game
import json
import socketio
import json
from aioredis import create_redis_pool
from ast import literal_eval

from game import GameRoom



sio = socketio.AsyncServer(async_mode='sanic')

room_list = {}
next_roomID = 1

def setup_socketio(app):
  sio.attach(app)



@sio.event
async def connect(sid, environ):
  try:
    HTTP_SID = environ['sanic.request'].cookies['session'] # KeyError occurs here
    redis = await create_redis_pool('redis://localhost')
    HTTPsession = await redis.get('session:' + HTTP_SID)
    redis.close()
    await redis.wait_closed()
  except KeyError: # occurs when request has no cookie named 'session'
    HTTPsession = None

  if HTTPsession is None:
    raise ConnectionRefusedError('not logged in')
  HTTPsession = HTTPsession.decode('ascii')
  HTTPsession = HTTPsession.replace('true', 'True')
  HTTPsession = literal_eval(HTTPsession)
  if not HTTPsession.get('logged_in'):
    raise ConnectionRefusedError('not logged in')

  await sio.save_session(sid, HTTPsession)
  user = await sio.get_session(sid)
  print('user connected:', user['username'])



@sio.event
async def disconnect(sid):
  user = await sio.get_session(sid)
  print('user disconnected: ', user.get('username'))
  if 'room' in user:
    await leave_GameRoom(sid, None)


@sio.event
async def enter_GameRoom(sid, data):
  assert 'roomID' in data
  user = await sio.get_session(sid)
  roomID = data['roomID']
  if roomID in room_list:
    if room_list[roomID].isFull():
      await sio.emit('failed_to_enter_GameRoom', {
        'reason': 'full',
      })
    else:
      sio.enter_room(sid, roomID)
      user['room']=roomID
      room = room_list[roomID]
      room.members.append(sid)
      await sio.save_session(sid, user)
      await sio.emit('enter_GameRoom_success', roomID)
      await sio.emit('notification', {'type': 'enter',
                                      'who': user['username']},
                                      room=roomID)
      print(user['username'], 'enters room #', roomID)
  else:
    print(user['username'], 'fails to enter room #', roomID)
    await sio.emit('failed_to_enter_GameRoom', {
      'reason': 'No such room',
    })

@sio.event
async def leave_GameRoom(sid, data):
  user = await sio.get_session(sid)
  assert 'room' in user
  roomID = user['room']
  room = room_list[roomID]
  room.members.remove(sid)
  print(user['username'], 'left room #', roomID)
  del user['room']
  await sio.save_session(sid, user)
  if not room.members:
    del room_list[roomID]

@sio.event
async def create_GameRoom(sid, data):
  # TODO: password
  global next_roomID
  assert type(data) is dict
  assert 'title' in data
  assert 'capacity' in data
  user = await sio.get_session(sid)
  print(user['username'], 'creates room #', next_roomID)
  room_list[next_roomID]=GameRoom(title=data['title'],
                                  capacity=data['capacity'],
                                  host=sid)
  print(room_list)
  await sio.emit('create_GameRoom_success', next_roomID)
  next_roomID+=1



@sio.event
async def message(sid, data):
  assert type(data)==str
  async with sio.session(sid) as user:
    to_send = {
      'who': user['username'],
      'message': data,
    }
    await sio.emit('message',
                   to_send,
                   room=user['room'])
