# import asyncio
import flask
import flask_socketio
from engineio.payload import Payload
from . import manager

Payload.max_decode_packets = 100000

def build(app):
    # Build Socket Server
    socket_server = flask_socketio.SocketIO(app, cors_allowed_origins='*')

    # Build Client Manager
    client_manager = manager.ClientManager(socket_server)

    # handles all namespaces without an explicit error handler
    @socket_server.on_error_default
    def default_error_handler(e):
        sid = flask.request.sid
        print('error ... ', e, sid)

    # connect
    @socket_server.on('connect')
    def handle_connect():
        sid = flask.request.sid
        print('connecting ... ', sid)
        client_manager.connected(sid)

    # disconnect
    @socket_server.on('disconnect')
    def handle_disconnect():
        try:
            sid = flask.request.sid
            print('disconnecting ... ', sid)
            client_manager.disconnected(sid)
        except Exception as error:
            print('error disconnecting ... ', sid)
            print(error)

    # pulse : (optional) { available_cameras : boolean }
    @socket_server.on('pulse')
    def handle_pulse(data):
        sid = flask.request.sid
        client_manager.pulse(sid)
        if 'available_cameras' in data:
            if data['available_cameras']:
                client_manager.send_available_cameras(sid)

    # authorize : { user_id : string, client_type : string, client_key : string }
    @socket_server.on('authorize')
    def handle_auth(data):
        sid = flask.request.sid
        print('authorizing ... ', sid, data)
        client = client_manager.authenticate_user(sid, data)
        if client is not None:
            return '200'
        return '401'

    # produce-frame : { camera_id : string, frame : base64.jpg }
    @socket_server.on('produce-frame')
    def handle_broadcast(data):
        sid = flask.request.sid
        if 'camera_id' in data and 'frame' in data:
            client_manager.put_frame(
                sid,
                data['camera_id'],
                data['frame']
            )
        return '200'

    # consume-view : { producers : { producer_id : [camera_list], ... } }
    @socket_server.on('consume-view')
    def handle_view(data):
        sid = flask.request.sid
        print('setting camera views ... ', data)
        if 'producers' in data:
            if client_manager.set_cameras(sid, data['producers']):
                return '202'
        return '204'

    # { connections : { camera_id : { sdp : sdp, type : type } }, ... } }
    @socket_server.on('consume-rtc')
    def handle_rtc_consume(data):
        sid = flask.request.sid
        print('consume-rtc ... ', data)
        # sends sdp & type to each specified producer
        cameras = data['connections']
        for camera_id, info in cameras.items():
            client_manager.connect_camera(sid, camera_id, info['sdp'], info['type'])
        # producer will initiate RTC Peer
        # producer will then send produce-rtc, with relevant info to be sent back to client for

    # { requested_session : peer_session_id, camera_id : camera_id, sdp : sdp, type : type }
    @socket_server.on('produce-rtc')
    def handle_rtc_produce(data):
        print('produce-rtc ... ', data)
        # will send sdp and type back as answer for consumer to finish establishing a connection
        socket_server.emit('connected-rtc', {'camera_id': data['camera_id'], 'sdp': data['sdp'], 'type': data['type']}, room=data['requested_session'])

    client_manager.start()
    return app

    # @socket_server.on('message')
    # def handle_message(message):
    #     sid = flask.request.sid
    #     socket_server.emit('message', message, room=sid)

    # @socket_server.on('create or join')
    # def handle_room(room):
    #     sid = flask.request.sid
    #     num_clients = len(flask_socketio.room(room))
    #     if num_clients == 0:
    #         flask_socketio.join_room(room)
    #         socket_server.emit('created', room, room=sid)
    #     elif num_clients <= 10:
    #         socket_server.emit('join', room, room=room)
    #         flask_socketio.join_room(room)
    #         socket_server.emit('joined', room, room=sid)
    #     else:
    #         socket_server.emit('full', room, room=sid)
    #     socket_server.emit('emit(): client ' + sid + ' joined room ' + room, room=sid)
    #     socket_server.emit('broadcast(): client ' + sid + ' joined room ' + room)
