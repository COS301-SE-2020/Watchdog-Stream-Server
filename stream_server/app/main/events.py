import socketio
from . import manager


socket_server = socketio.Server(async_mode='eventlet')
client_manager = manager.ClientManager(socket_server)


# connect : Client Connects
@socket_server.event
def connect(sid, environ):
    print('connecting ... ', sid)


# disconnect : Client Disconnects
@socket_server.event
def disconnect(sid):
    print('disconnecting ... ', sid)
    session = socket_server.get_session(sid)
    client_manager.remove_client(session['client_id'])


# connect : Client Connects
# data : { user_id : string, client_type : string, client_key : string }
@socket_server.on('authorize')
def handle_auth(sid, data):
    print('authorizing ... ', data)
    client = client_manager.authenticate_user(sid, data)
    if client is not None:
        socket_server.save_session(sid, {'client_id': client.id, 'user_id': client.user_id})
    else:
        raise ConnectionRefusedError('authentication failed')


# produce-frame : HCP-client sending encoded frame.jpg (continuous)
# data : { camera_id : string, frame : base64.jpg }
@socket_server.on('produce-frame')
def handle_broadcast(sid, data):
    session = socket_server.get_session(sid)
    print('producing frame ... ', data)
    client_manager.put_frame(
        session['user_id'],
        data['camera_id'],
        data['frame']
    )
    return 'OK'


# consume-view : Sets the respective cameras a consumer wants to stream
# data : { camera_list : [] }
@socket_server.on('consume-view')
def handle_view(sid, data):
    session = socket_server.get_session(sid)
    print('setting camera views ... ', data)
    print('\tcamera-list : ', data['camera_list'])
    client_manager.set_cameras(session['client_id'], data['camera_list'])
    return 'OK'
