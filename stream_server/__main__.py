import os
from app import create_app
from flask import Flask, render_template, request, session, Markup, current_app, jsonify
from flask_socketio import emit, SocketIO
import eventlet

# eventlet.monkey_patch()
app = create_app()


if __name__ == '__main__':
    try:
        app_host = '0.0.0.0'
        app_port = 8080

        # HTTPS
        # eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen((app_host, int(app_port))),
        #                                        certfile='stream_server.crt',
        #                                        keyfile='stream_server.key',
        #                                        server_side=True),
        #                      app)
        # HTTP
        eventlet.wsgi.server(eventlet.listen((app_host, int(app_port))), app)

    except Exception as e:
        print(e)
