import eventlet
from app import create_app

app = create_app(debug=True)


def main():
    eventlet.wsgi.server(eventlet.listen(('13.245.35.130', 80)), app)


if __name__ == '__main__':
    main()
