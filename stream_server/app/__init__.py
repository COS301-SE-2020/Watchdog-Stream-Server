# import socketio
from flask import Flask
from .main.events import build

def create_app():
    # app = socketio.WSGIApp(socket_server)
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "200"

    app = build(app)

    return app
