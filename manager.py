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
USER_CAMERAS_ONLINE = {}
SID_USER_REGISTRY = SafeDict("Sid's to User Ids")
SERVER_HEALTH = {'connection_health': 0}


def add_connection_health(value: int):
    with LOCK:
        SERVER_HEALTH['connection_health'] += value
        return 100-SERVER_HEALTH['connection_health']


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
            # If producer, register this to the user_id
            user_id = SID_USER_REGISTRY.get(sid)
            if user_id not in USER_CAMERAS_ONLINE:
                USER_CAMERAS_ONLINE[user_id] = []
            USER_CAMERAS_ONLINE[user_id].append(camera_id)
            print(USER_CAMERAS_ONLINE[user_id])

        if camera_id not in register:
            register[camera_id] = {}
        if sid not in register[camera_id]:
            register[camera_id][sid] = {}
            CLIENT_TYPES.add(sid, client_type)
            join_room(room_name(camera_id), sid)


def remove_camera_connection(sid, sio):
    """
    Removes client from all cameras
    :param sio: Socket Connection
    :param sid: Socket id
    :return:
    """
    with LOCK:
        client_type = CLIENT_TYPES.get(sid)
        register = None
        room_name = None
        other_room = None
        user_id = SID_USER_REGISTRY.get(sid)

        if client_type == CONSUMER:
            register = CAMERA_CONSUMERS
            room_name = consumer_room
            other_room = producer_room
        else:
            register = CAMERA_PRODUCERS
            room_name = producer_room
            other_room = consumer_room

        for camera_id in register:
            if sid in register[camera_id]:
                del register[camera_id][sid]
                CLIENT_TYPES.remove(sid)
                sio.emit(f'{client_type}-shutdown-camera', room=other_room(camera_id), data={
                    'camera_id': camera_id
                })
                leave_room(room_name(camera_id), sid)
                if client_type == PRODUCER and user_id in USER_CAMERAS_ONLINE:
                    if camera_id in USER_CAMERAS_ONLINE[user_id]:
                        USER_CAMERAS_ONLINE[user_id].remove(camera_id)


def build(app):
    sio = flask_socketio.SocketIO(app, cors_allowed_origins='*')

    @sio.on('connect')
    def connect():
        print(f"connected: \t{flask.request.sid}\n\tSERVER HEALTH: {add_connection_health(1)}")

    @sio.on('disconnect')
    def disconnect():
        sid = flask.request.sid
        remove_camera_connection(sid, sio)
        SID_USER_REGISTRY.remove(sid)
        print(f'disconnect: \t{sid}\n\tSERVER HEALTH: {add_connection_health(-1)}')

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

    @sio.on('ice-connection-failed')
    def failed_ice(data):
        sid = NEGOTIATIONS.get_and_remove(data['token'])
        sio.emit(event='camera-connection-failed', sid=sid, data={
            'code': 0,
            'reason': 'Failed to connect to Panel'
        })

    @sio.on('stream-connection-failure')
    def failed_connect_to_camera(data):
        sid = NEGOTIATIONS.get_and_remove(data['token'])
        sio.emit(event='camera-connection-failed', sid=sid, data={
            'code': 1,
            'reason': 'Panel Failed to connect to IP Camera'
        })

    @sio.on('register')
    def register_client(data=None):
        """
        Registers the sid to a user_id
        :param data: { user_id }
        :return:
        """
        SID_USER_REGISTRY.add(flask.request.sid, data['user_id'])
        print(f'registering: {data["user_id"]}')
        # Send back confirmation
        sio.emit(event='registered', sid=flask.request.sid, data={'user_id': data['user_id']})

    @sio.on('fetch-online-cameras')
    def available_views(data=None):
        sid = flask.request.sid
        user_id = SID_USER_REGISTRY.get(sid)
        if user_id in USER_CAMERAS_ONLINE:
            print(USER_CAMERAS_ONLINE[user_id])
            for camera_id in USER_CAMERAS_ONLINE[user_id]:
                join_room(consumer_room(camera_id), sid)
            sio.emit(event='cameras-online', sid=sid, data={'cameras': USER_CAMERAS_ONLINE[user_id], "user_id": user_id})
        else:
            print('Not found')
            sio.emit(event='cameras-online', sid=sid, data={'cameras': [], 'user_id': user_id})
