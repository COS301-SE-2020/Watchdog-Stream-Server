from . import client_manager, socket_server
# HCP-Client:
#   Will always try connecting
#   Will only broadcast if there are connected Mobile-clients for the same user-id
#       Receives Start/Stop signals to indicate if it should broadcast (sent from ClientManager)
#   When broacasting, will continuously send bytestreams of jpeg frames to fill its frame_buffer

# Mobile-Client:
#   Will only connect when wanting to view a livestream
#   Every client must go through the API Gateway, which will trigger the EC2 instance if it is inactive
#   Will draw the most up to date frame to its livestream view when sent an image
#       Will only be sent to client if its respective HCP-Client is present
#       If HCP-Client is inactive, it is set to active


# connect : Client Connects
#   Authenticate client
#       Check if HCP-client or Mobile-client
#           Assign to correct category in ClientManager
@socket_server.event
def connect(sid, environ):
    print('connecting on ', sid)


# disconnect : Client Disconnects
#   Disconnect client from ClientManager
#       If this is a Mobile-client, and the respective HCP-client now has 0 Mobile-clients, set it as inactive
@socket_server.event
def disconnect(sid):
    print('disconnect off ', sid)
    session = socket_server.get_session(sid)
    client_manager.remove_client(session['client_id'], session['user_id'])


# connect : Client Connects
#   Authenticate client
#       Check if HCP-client or Mobile-client
#           Assign to correct category in ClientManager
@socket_server.on('authorize')
def handle_auth(sid, data):
    print('authorize ', sid)
    client = client_manager.authenticate_user(sid, data)
    if client is None:
        raise ConnectionRefusedError('authentication failed')
    # Store client id in session, so that we know which client to manage when called
    socket_server.save_session(sid, {'client_id': client.id, 'user_id': client.user_id})


# broadcast : HCP-client sending encoded frame.jpg (continuous)
#   Add the frame to this HCP-clients buffer
@socket_server.on('broadcast')
def handle_broadcast(sid, data):
    print('broadcasting on ', sid)
    session = socket_server.get_session(sid)
    client_manager.put_frame(session['user_id'], data['frame'])
    return 'OK'


# view : Mobile-client wanting to start retrieving encoded frame.jpg's from its respective hcp (once-off)
#   Sets it respective HCP-Client as active (if it is not already)
#       Starts the sending of frames to the Mobile-client
# @socket_server.on('view')
# def handle_view(sid, data):
#     print(data)
#     session = socket_server.get_session(sid)
#     if client_manager.check_producer(session['id'], data['user_id']):
#         return 'OK'
#     return 'EMPTY'
