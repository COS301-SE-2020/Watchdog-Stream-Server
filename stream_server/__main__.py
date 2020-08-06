import eventlet
from app import create_app

app = create_app(debug=True)


def main():
    eventlet.wsgi.server(eventlet.listen(('ec2-13-245-35-130.af-south-1.compute.amazonaws.com', 8008)), app)


if __name__ == '__main__':
    main()
