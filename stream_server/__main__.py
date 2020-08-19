from flask import *
from flask_socketio import *
from app import create_app
import eventlet

eventlet.monkey_patch()
app = create_app()


if __name__ == '__main__':
    try:
        app_host = '0.0.0.0'
        app_port = 8080

        # HTTPS
        # eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen((app_host, int(app_port))),
        #                                        certfile='29742946_ec2-13-245-14-169.af-south-1.compute.amazonaws.com.cert',
        #                                        keyfile='29742946_ec2-13-245-14-169.af-south-1.compute.amazonaws.com.key',
        #                                        server_side=True),
        #                      app)
        # HTTP
        eventlet.wsgi.server(eventlet.listen((app_host, int(app_port))), app)

    except Exception as e:
        print(e)
