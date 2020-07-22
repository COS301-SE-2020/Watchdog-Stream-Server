import socketio
from user import start_broadcast, stop_broadcast, display_stream

socket_client = socketio.Client()

# Data : { active : boolean }
@socket_client.on('broadcast')
def toggle_broadcast(data):
    active = data['active']
    if active:
        start_broadcast(data['user_id'])
    else:
        stop_broadcast(data['user_id'])

# Data : { frame : string }
@socket_client.on('stream')
def accept_stream(data):
    image = data['frame']
    display_stream(data['user_id'], image)
