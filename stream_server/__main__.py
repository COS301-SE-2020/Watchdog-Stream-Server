import eventlet
from app import create_app

app = create_app(debug=True)


def main():
    eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('0.0.0.0', 8080)),
                                           certfile='https/certificate.crt',
                                           keyfile='https/private.key',
                                           server_side=True),
                         app)


if __name__ == '__main__':
    main()
