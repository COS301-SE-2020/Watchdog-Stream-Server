import eventlet
import eventlet.wsgi
import app
eventlet.monkey_patch()

server_app = app.create_app()


def main():
    try:
        app_host = '0.0.0.0'
        app_port = 5555
        eventlet.wsgi.server(eventlet.listen((app_host, int(app_port))), server_app, log=None, log_output=False)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
