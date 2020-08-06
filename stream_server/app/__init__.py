import socketio
from .main import socket_server

def create_app(debug=False):
    app = socketio.WSGIApp(socket_server)
    return app
