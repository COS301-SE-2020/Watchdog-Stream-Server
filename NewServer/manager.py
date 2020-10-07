import os
import flask
import flask_socketio
from flask_socketio import join_room, leave_room

from safe_dictionary import SafeDict

ROOT = os.path.dirname(__file__)
USERS = SafeDict(name='Registered Users')
SID_ROOMS = SafeDict(name='Socket Rooms')

CAMERA_CONSUMERS = SafeDict(name='CAMERA_CONSUMERS')
CAMERA_PRODUCERS = SafeDict(name='CAMERA_PRODUCERS')

PRODUCERS = SafeDict(name='Producers')
CONSUMERS = SafeDict(name='Consumers')
CLIENTS = SafeDict(name='Client Pools')
CLIENTS.add('producer', PRODUCERS)
CLIENTS.add('consumer', CONSUMERS)


def build(app):
    sio = flask_socketio.SocketIO(app, cors_allowed_origins='*')

    @sio.on('connect')
    def connect():
        print("connected: ", flask.request.sid)

    @sio.on('disconnect')
    def disconnect():
        sid = flask.request.sid
        user_id = SID_ROOMS.get(sid)
        print(f'disconnect: \t{sid}\n\t{user_id}')
        if user_id:
            leave_room(sid, user_id)

    @sio.on('register')
    def registry_handler(params):
        """
        Registers users and classifies them as consumers and producers
        :param params: {
            "user_id", "client_type", "data"
        }
        :return: web.Response
        """
        print(params['user_id'])
        sid = flask.request.sid
        user_id = params['user_id']
        client_type = params['client_type']

        user = SID_ROOMS.get(sid)

        if user == user_id:
            if CLIENTS.get(client_type).get(user_id):
                sio.emit('registered', {
                    'status': True,
                    'code': 3,
                    'message': f'{client_type}: {user_id} already registered.'
                })
                print(CLIENTS.get(client_type))
            else:
                CLIENTS.get(client_type).add(user_id, params['data'])
                SID_ROOMS.add(sid, user_id)
                join_room(sid, user_id)
                sio.emit('registered', {
                    'status': True,
                    'code': 0,
                    'message': f'{client_type}: {user_id} registered.'
                })
                print(CLIENTS.get(client_type))
        else:
            USERS.add(user_id, sid)
            CLIENTS.get(client_type).add(user_id, params['data'])
            SID_ROOMS.add(sid, user_id)
            join_room(sid, user_id)
            sio.emit('registered', {
                'status': True,
                'code': 1,
                'message': f'{client_type}: {user_id} registered.'
            })
            print(CLIENTS.get(client_type))

    @sio.on('negotiate')
    def request_view(data):
        """

        :param data: { camera_id }
        :return:
        """
        print('RECEIVED NEGOTIATE...')
        producer = CAMERA_PRODUCERS.get(data['camera_id'])

        # if not camera:
        #     resp['available'] = False
        #     sio.emit('view-unavailable', resp)
        # else:
        CAMERA_CONSUMERS.add(data['camera_id'], flask.request.sid)
        if producer:
            print('EMITTING OFFER...')
            sio.emit('offer', sid=producer, data={
                'camera_id': data['camera_id'],
                'offer': data['offer']
            })

    @sio.on('view-available')
    def produce_view(data):
        """

        :param data: { camera_id, camera (rtc) }
        :return:
        """
        print(f'Making View Available: {data["camera_id"]}')
        CAMERA_PRODUCERS.add(data['camera_id'], flask.request.sid)
        sio.emit('camera-available', {
            "camera_id": data['camera_id']
        })

    @sio.on('answer')
    def send_answer_back(data):
        print('RECEIVED ANSWER FROM PRODUCER...')
        camera_id = data['camera_id']
        sid = CAMERA_CONSUMERS.get(camera_id)
        print('SENDING BACK TO CONSUMER...')
        sio.emit(sid=sid, event='producer-answer', data={'camera_id': camera_id, 'answer': data['answer']})
