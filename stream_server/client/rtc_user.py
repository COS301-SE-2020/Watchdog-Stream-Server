import socketio
import logging
import urllib3
import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

CLIENT_KEY = 'supersecure'
URL = 'http://127.0.0.1:5555'


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger('pc')


class VideoTransformTrack(MediaStreamTrack):
    kind = 'video'

    def __init__(self):
        super().__init__()  # don't forget this!
        self.frame = 'no-frame'
        with open('206379419296196619.jpg', 'rb') as file:
            self.frame = file

    async def recv(self):
        return self.frame


# Front-End Client Asbtract Class
class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.socket = socketio.Client(ssl_verify=False)
        self.socket.connect(URL)
        self.pcs = {}

        # Data : { user_id : string, camera_list : string }
        @self.socket.on('activate-broadcast')
        def activate_broadcast(data):
            print('\tEVENT : activating broadcast ... ', data)
            self.activate(data['camera_list'])

        # Data : { user_id : string, camera_list : string }
        @self.socket.on('deactivate-broadcast')
        def deactivate_broadcast(data):
            print('\tEVENT : deactivating broadcast ... ', data)
            self.deactivate()

        # Data : { camera_id : string, frame : string }
        @self.socket.on('consume-frame')
        def consume_frame(data):
            print('\tEVENT : consuming frame ... ', data)
            image = data['frame']
            self.consume(image)

        @self.socket.on('available-views')
        def available_views(data):
            print('\tEVENT : available views ... ', data)
            # self.set_cameras(data['producers'])

        @self.socket.on('connect-rtc')
        def connect_offer(data):
            print('\tEVENT : connect-rtc ... ', data)
            if self.get_type() == 'producer':
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.offer(data['connection']))

        @self.socket.on('connected-rtc')
        def connected_rtc(data):
            print('\tEVENT : connected-rtc ... ', data)
            if self.get_type() == 'consumer':
                self.ask(data)


# Front-End Producer Client
class Producer(User):
    def __init__(self, user_id, producer_id, available_cameras):
        super(Producer, self).__init__(user_id)
        self.active = False
        self.camera_list = []
        self.send_count = 0
        self.producer_id = producer_id
        self.socket.emit('authorize', {
            'user_id': self.user_id,
            'client_type': 'producer',
            'producer_id': self.producer_id,
            'available_cameras': available_cameras,
            'client_key': CLIENT_KEY
        })

        # self.player = VideoTransformTrack()
        self.player = MediaPlayer("rtsp://10.0.0.109:8080/h264_ulaw.sdp", options={"framerate": "30", "video_size": "640x480"})

    # Start HCP Client Producer
    def activate(self, camera_list):
        self.active = True
        for id in camera_list:
            self.camera_list.append(id)

    # Stop HCP Client Producer
    def deactivate(self):
        self.active = False
        self.camera_list = []

    # Send frame through to Server
    def produce(self, camera_id, frame):
        # if self.active and camera_id in self.camera_list:
        #     self.player.frame = frame
        self.send_count = self.send_count + 1

    def get_list(self):
        return self.camera_list

    async def offer(self, request):
        print('OFFER')
        print(request)
        camera_id = request['camera_id']
        peer_session_id = request['peer_session_id']
        offer = RTCSessionDescription(sdp=request['sdp'], type=request['type'])

        pc = RTCPeerConnection()
        self.pcs[camera_id] = pc

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange():
            print('ICE connection state is %s' % pc.iceConnectionState)
            if pc.iceConnectionState == 'failed':
                await pc.close()
                del self.pcs[camera_id]

        await pc.setRemoteDescription(offer)
        for t in pc.getTransceivers():
            if t.kind == 'video':
                pc.addTrack(self.player.video)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        self.socket.emit('produce-rtc', {
            'requested_session': peer_session_id,
            'camera_id': camera_id,
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        })

    def get_type(self):
        return 'producer'

# Front-End Consumer Client
class Consumer(User):
    def __init__(self, user_id):
        super(Consumer, self).__init__(user_id)
        self.buffer = None
        self.receive_count = 0
        print('authorize', {'user_id': self.user_id, 'client_type': 'consumer', 'client_key': CLIENT_KEY})
        self.socket.emit('authorize', {'user_id': self.user_id, 'client_type': 'consumer', 'client_key': CLIENT_KEY})

    def set_cameras(self, producers):
        print('consume-view', {'producers': producers})
        self.socket.emit('consume-view', {'producers': producers})

    # Mobile Client Consumer Draws frame data to screen
    def consume(self, data):
        self.buffer = data
        print(self.buffer)
        self.receive_count = self.receive_count + 1

    # async def ask(self, request):
        # camera_id = request['camera_id']

        # config = {'sdpSemantics': 'unified-plan'}
        # config.iceServers = [{'urls': ['stun:stun.l.google.com:19302']}]

        # pc = RTCPeerConnection(config)
        # # self.pcs.add(pc)
        # self.pcs[camera_id] = pc

        # @pc.on('track')
        # async def on_track(evt):
        #     print(evt)

        # pc.addTransceiver('video', {'direction': 'recvonly'})
        # offer = pc.createOffer()
        # pc.setLocalDescription(offer)

        # self.socket.emit('consume-rtc', {'connections': connections})

    def get_type(self):
        return 'consumer'
