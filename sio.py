import asyncio
import game
import json
import socketio
from aioredis import create_redis_pool
from ast import literal_eval

sio = socketio.AsyncServer(async_mode='sanic')



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
  except KeyError:
    HTTPsession = None# request has no cookie named 'session'

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



@sio.event
async def room_request(sid, data):
  assert type(data)==str
  sio.enter_room(sid, data)
  user = await sio.get_session(sid)
  user.update({'room': data})
  await sio.save_session(sid, user)
  await sio.emit('message',
                 user['username'] + '님이 입장했습니다.',
                 room=user['room'])



@sio.event
async def message(sid, data):
  assert type(data)==str
  async with sio.session(sid) as user:
    await sio.emit('message',
                   user['username']+': '+data,
                   room=user['room'])
