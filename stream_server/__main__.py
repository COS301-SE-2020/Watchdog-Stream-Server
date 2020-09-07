import eventlet
from app import app


eventlet.monkey_patch()

server_app = app.create_app()


def main():
    try:
        app_host = '127.0.0.1'
        app_port = 8080
        eventlet.wsgi.server(eventlet.listen((app_host, int(app_port))), server_app)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
