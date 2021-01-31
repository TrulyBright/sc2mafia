import aioredis
import aiohttp
from sanic import Sanic
from jinja2_sanic import setup as setup_jinja2
from jinja2 import FileSystemLoader
from sanic_session import Session, AIORedisSessionInterface

from routes import setup_routes
from sio import setup_socketio

app = Sanic("sc2mafia")

# sanic_session initialization
@app.listener("before_server_start")
async def session_init(app, loop):
    app.redis = await aioredis.create_redis_pool("redis://localhost")
    Session().init_app(app, interface=AIORedisSessionInterface(app.redis))
    app.oauth_client = aiohttp.ClientSession()

@app.listener('after_server_stop')
async def client_close(app, loop):
    await app.oauth_client.close()

# setup
app.static("/static", "./static")
setup_routes(app)
setup_jinja2(app, loader=FileSystemLoader("templates/"))
setup_socketio(app)
