import asyncio
import flask
import flask_socketio
from engineio.payload import Payload
from . import manager

Payload.max_decode_packets = 1000

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def build(app):
    # Build Socket Server
    socket_server = flask_socketio.SocketIO(app, cors_allowed_origins='*')

    # Build Client Manager
    client_manager = manager.ClientManager(socket_server)

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

    # handles all namespaces without an explicit error handler
    @socket_server.on_error_default
    def default_error_handler(e):
        sid = flask.request.sid
        print('error ... ', e, sid)

    # pulse : tells server you're still connected
    @socket_server.on('pulse')
    def handle_pulse(data):
        sid = flask.request.sid
        client_manager.pulse(sid)

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
            asyncio.get_event_loop().run_until_complete(client_manager.put_frame(
                sid,
                data['camera_id'],
                data['frame']
            ))
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

    client_manager.start()
    return app
