from sanic import Sanic
# from sanja import conf_app, render
from jinja2_sanic import setup as setup_jinja2
from jinja2 import FileSystemLoader
# from sanic.websocket import WebSocketProtocol
# from sanic_jwt_extended import JWT
import aioredis
from sanic_session import Session, AIORedisSessionInterface

from routes import setup_routes
from sio import setup_socketio

app = Sanic(__name__)

# sanic_session initialization
@app.listener('before_server_start')
async def session_init(app, loop):
  app.redis = await aioredis.create_redis_pool('redis://localhost')
  Session().init_app(app, interface=AIORedisSessionInterface(app.redis))


#setup
app.static('/static', './static')
setup_routes(app)
setup_socketio(app)
setup_jinja2(app, loader=FileSystemLoader('templates/'))
# conf_app(app, loader=FileSystemLoader('templates/')) #jinja2 setup
# with JWT.initialize(app) as manager:
#   manager.config.secret_key='secret_key'


#run
if __name__ == '__main__':
  app.run(host='localhost', port=8080)
