import socketio
import logging
import urllib3
import uuid
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
# from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder

CLIENT_KEY = 'supersecure'
URL = 'http://127.0.0.1:5555'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger("pc")


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track

    async def recv(self):
        # frame = await self.track.recv()
        frame = 'wwwwwwwww'
        return frame


# Front-End Client Asbtract Class
class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.socket = socketio.Client(ssl_verify=False)
        self.socket.connect(URL)
        self.pcs = set()

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

        @self.socket.on('rtc-connect')
        def connect_offer(data):
            print('\tEVENT : rtc-connect ... ', data)
            self.offer(data)

    async def offer(self, request):
        print(request)
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        pc = RTCPeerConnection()
        self.pcs.add(pc)

        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            print("ICE connection state is %s" % pc.iceConnectionState)
            if pc.iceConnectionState == "failed":
                await pc.close()
                self.pcs.discard(pc)

        player = VideoTransformTrack("/dev/video0")

        await pc.setRemoteDescription(offer)
        for t in pc.getTransceivers():
            if t.kind == "video":
                pc.addTrack(player)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)


# Front-End Producer Client
class Producer(User):
    def __init__(self, user_id, producer_id, available_cameras):
        super(Producer, self).__init__(user_id)
        self.active = False
        self.camera_list = []
        self.send_count = 0
        print('authorize', {
            'user_id': self.user_id,
            'client_type': 'producer',
            'producer_id': producer_id,
            'available_cameras': available_cameras,
            'client_key': CLIENT_KEY
        })
        self.socket.emit('authorize', {
            'user_id': self.user_id,
            'client_type': 'producer',
            'producer_id': producer_id,
            'available_cameras': available_cameras,
            'client_key': CLIENT_KEY
        })

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
        if self.active and camera_id in self.camera_list:
            print('produce-frame', {'camera_id': camera_id, 'frame': frame})
            self.socket.emit('produce-frame', {'camera_id': camera_id, 'frame': frame})
        self.send_count = self.send_count + 1

    def get_list(self):
        return self.camera_list


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
