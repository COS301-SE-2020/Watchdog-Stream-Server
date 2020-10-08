import os
import flask
import flask_socketio
from flask_socketio import join_room, leave_room
from threading import Lock
from safe_dictionary import SafeDict
import random, string

LOCK = Lock()
CAMERA_CONSUMERS = {}
CAMERA_PRODUCERS = {}
CLIENT_TYPES = SafeDict('Client Types')
CONSUMER = "consumer"
PRODUCER = "producer"
NEGOTIATIONS = SafeDict()


def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def consumer_room(camera_id):
    return f'consumers_{camera_id}'


def producer_room(camera_id):
    return f'producers_{camera_id}'


def add_camera_connection(camera_id, client_type, sid):
    with LOCK:
        register = None
        room_name = None
        if client_type == CONSUMER:
            register = CAMERA_CONSUMERS
            room_name = consumer_room
        else:
            register = CAMERA_PRODUCERS
            room_name = producer_room

        if camera_id not in register:
            register[camera_id] = {}
        if sid not in register[camera_id]:
            register[camera_id][sid] = {}
            CLIENT_TYPES.add(sid, client_type)
            join_room(room_name(camera_id), sid)


def remove_camera_connection(sid):
    """
    Removes client from all cameras
    :param sid:
    :return:
    """
    with LOCK:
        client_type = CLIENT_TYPES.get(sid)
        register = None
        room_name = None
        if client_type == CONSUMER:
            register = CAMERA_CONSUMERS
            room_name = consumer_room
        else:
            register = CAMERA_PRODUCERS
            room_name = producer_room

        for camera_id in register:
            if sid in register[camera_id]:
                del register[camera_id][sid]
                CLIENT_TYPES.remove(sid)
                leave_room(room_name(camera_id), sid)


def build(app):
    sio = flask_socketio.SocketIO(app, cors_allowed_origins='*')

    @sio.on('connect')
    def connect():
        print("connected: \t", flask.request.sid)

    @sio.on('disconnect')
    def disconnect():
        sid = flask.request.sid
        remove_camera_connection(sid)
        print(f'disconnect: \t{sid}')

    # @sio.on('register')
    # def registry_handler(params):
    #     """
    #     Registers users and classifies them as consumers and producers
    #     :param params: {
    #         "user_id", "client_type", "data"
    #     }
    #     :return: web.Response
    #     """
    #     print(params['user_id'])
    #     sid = flask.request.sid
    #     user_id = params['user_id']
    #     client_type = params['client_type']
    #
    #     user = SID_ROOMS.get(sid)
    #
    #     if user == user_id:
    #         if CLIENTS.get(client_type).get(user_id):
    #             sio.emit('registered', {
    #                 'status': True,
    #                 'code': 3,
    #                 'message': f'{client_type}: {user_id} already registered.'
    #             })
    #             print(CLIENTS.get(client_type))
    #         else:
    #             CLIENTS.get(client_type).add(user_id, params['data'])
    #             SID_ROOMS.add(sid, user_id)
    #             join_room(sid, user_id)
    #             sio.emit('registered', {
    #                 'status': True,
    #                 'code': 0,
    #                 'message': f'{client_type}: {user_id} registered.'
    #             })
    #             print(CLIENTS.get(client_type))
    #     else:
    #         USERS.add(user_id, sid)
    #         CLIENTS.get(client_type).add(user_id, params['data'])
    #         SID_ROOMS.add(sid, user_id)
    #         join_room(sid, user_id)
    #         sio.emit('registered', {
    #             'status': True,
    #             'code': 1,
    #             'message': f'{client_type}: {user_id} registered.'
    #         })
    #         print(CLIENTS.get(client_type))

    @sio.on('negotiate')
    def request_view(data):
        """
        Start the rtc stream service and register sid on the camera
        :param data: { camera_id }
        :return:
        """
        print(f'NEGOTIATING: {data["camera_id"]}')
        token = generate_token()
        NEGOTIATIONS.add(token, flask.request.sid)
        print(f'SENDING OFFER TO: {data["camera_id"]}')
        sio.emit('offer', data={
            'camera_id': data['camera_id'],
            'offer': data['offer'],
            'token': token
        }, room=producer_room(data['camera_id']))

    @sio.on('make-available')
    def producer_view(data):
        """

        :param data: { camera_id, camera (rtc) }
        :return:
        """
        print(f'MAKE_AVAILABLE: {data["camera_id"]}')
        add_camera_connection(data['camera_id'], PRODUCER, flask.request.sid)

        sio.emit('camera-available', {
            "camera_id": data['camera_id']
        }, room=consumer_room(data['camera_id']))

    @sio.on('answer')
    def send_answer_back(data):
        print(f'RECEIVED ANSWER: {data["camera_id"]}')
        camera_id = data['camera_id']
        token = data['token']
        sid = NEGOTIATIONS.get_and_remove(token)
        print(f'SENDING ANSWER TO PRODUCER: {data["camera_id"]}')
        sio.emit(sid=sid, event='producer-answer', data={'camera_id': camera_id, 'answer': data['answer']})
