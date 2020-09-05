import eventlet
from app import create_app

eventlet.monkey_patch()

app = create_app()

if __name__ == '__main__':
    try:
        app_host = '127.0.0.1'
        app_port = 8080

        eventlet.wsgi.server(eventlet.listen((app_host, int(app_port))), app)

    except Exception as e:
        print(e)
