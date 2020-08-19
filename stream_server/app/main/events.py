import flask
import flask_socketio
from . import manager


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

    # disconnect
    @socket_server.on('disconnect')
    def handle_disconnect():
        sid = flask.request.sid
        print('disconnecting ... ', sid)
        client_manager.remove_client(sid)

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
        print('producing frame ... ', sid, data)
        if 'camera_id' in data and 'frame' in data:
            client_manager.put_frame(
                sid,
                data['camera_id'],
                data['frame']
            )
        return '200'

    # consume-view : { producer_id : string, camera_list : [] }
    @socket_server.on('consume-view')
    def handle_view(data):
        sid = flask.request.sid
        print('setting camera views ... ', data)
        if 'producer_id' in data and 'camera_list' in data:
            if client_manager.set_cameras(sid, data['producer_id'], data['camera_list']):
                return '202'
        return '204'

    return app
