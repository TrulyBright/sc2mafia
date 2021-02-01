import aioredis
import aiohttp
import logging
from logging.handlers import RotatingFileHandler
from sanic import Sanic
from sanic.log import logger
from jinja2_sanic import setup as setup_jinja2
from jinja2 import FileSystemLoader
from sanic_session import Session, AIORedisSessionInterface

from routes import setup_routes
from sio import setup_socketio

app = Sanic("sc2mafia")

# sanic_session and logger initialization
@app.listener("before_server_start")
async def session_and_logger_init(app, loop):
    # session
    app.redis = await aioredis.create_redis_pool("redis://localhost")
    Session().init_app(app, interface=AIORedisSessionInterface(app.redis))
    app.oauth_client = aiohttp.ClientSession()
    # logger
    handler = RotatingFileHandler("sc2mafia.log", maxBytes=16*1024*1024, backupCount=64)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="%(asctime)s - (%(name)s)[%(levelname)s]: %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

@app.listener('after_server_stop')
async def client_close(app, loop):
    await app.oauth_client.close()

# setup
app.static("/static", "./static")
setup_routes(app)
setup_jinja2(app, loader=FileSystemLoader("templates/"))
setup_socketio(app)

if __name__ == '__main__':
    app.run(port=8000)
