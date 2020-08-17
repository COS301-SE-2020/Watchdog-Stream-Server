import eventlet
from app import create_app

app = create_app(debug=True)


def main():
    eventlet.wsgi.server(
        eventlet.wrap_ssl(
            eventlet.listen(('0.0.0.0', 443)),
            certfile='https/88543630_ec2-13-245-14-169.af-south-1.compute.amazonaws.com443.cert',
            keyfile='https/88543630_ec2-13-245-14-169.af-south-1.compute.amazonaws.com443.key',
            server_side=True
        ), app
    )


if __name__ == '__main__':
    main()
