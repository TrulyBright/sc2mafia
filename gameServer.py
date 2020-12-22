from sanic import Sanic

from sio import setup_socketio

app = Sanic(__name__)
setup_socketio(app)

app.config["CORS_SUPPORTS_CREDENTIALS"] = True

if __name__ == "__main__":
    app.run(host="localhost", port="8090")
