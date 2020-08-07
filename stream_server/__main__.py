import eventlet
from app import create_app

app = create_app(debug=True)


def main():
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)


if __name__ == '__main__':
    main()
