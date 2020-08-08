import asyncio
import socketio
from . import manager

socket_server = socketio.Server(async_mode='eventlet')
client_manager = manager.ClientManager(socket_server)

# connect
@socket_server.event
def connect(sid, environ):
    print('connecting ... ', sid)

# disconnect
@socket_server.event
def disconnect(sid):
    print('disconnecting ... ', sid)
    client_manager.remove_client(sid)

# authorize : { user_id : string, client_type : string, client_key : string }
@socket_server.on('authorize')
def handle_auth(sid, data):
    print('authorizing ... ', data)
    client = client_manager.authenticate_user(sid, data)
    if client is not None:
        socket_server.save_session(sid, {'client_id': client.id, 'user_id': client.user_id})
        return '200'
    return '401'

# produce-frame : { camera_id : string, frame : base64.jpg }
@socket_server.on('produce-frame')
def handle_broadcast(sid, data):
    session = socket_server.get_session(sid)
    print('producing frame ... ', data)
    if 'user_id' in session and 'client_id' in session:
        if 'camera_id' in data and 'frame' in data:
            asyncio.get_event_loop().run_until_complete(client_manager.put_frame(
                session['user_id'],
                session['client_id'],
                data['camera_id'],
                data['frame']
            ))
    return '200'

# consume-view : { producer_id : string, camera_list : [] }
@socket_server.on('consume-view')
def handle_view(sid, data):
    session = socket_server.get_session(sid)
    print('setting camera views ... ', data)
    if 'client_id' in session:
        if 'producer_id' in data and 'camera_list' in data:
            if client_manager.set_cameras(session['client_id'], data['producer_id'], data['camera_list']):
                return '202'
    return '204'
