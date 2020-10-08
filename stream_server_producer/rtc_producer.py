import asyncio
import platform

import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

URL = "http://127.0.0.1:8081"


class RTCConnectionHandler:
    def __init__(self, camera_id, user_id):
        self.pc = {}
        self.pcs = set()
        self.socket = socketio.AsyncClient(ssl_verify=False)
        self.user_id = user_id
        self.camera_id = camera_id

    async def start(self):
        await self.socket.connect(URL)

        @self.socket.on('offer')
        async def process_offer(params):
            if params['camera_id'] != self.camera_id:
                return
            print('RECEIVED OFFER...')
            # params = await request.json()
            offer = RTCSessionDescription(sdp=params['offer']["sdp"], type=params['offer']["type"])

            pc = RTCPeerConnection()
            self.pc[params['camera_id']] = pc
            self.pcs.add(self.pc[params['camera_id']])

            @pc.on("iceconnectionstatechange")
            async def on_iceconnectionstatechange():
                print("ICE connection state is %s" % pc.iceConnectionState)
                if pc.iceConnectionState == "failed":
                    await pc.close()
                    self.pcs.discard(pc)

            # open media source
            options = {"framerate": "30"}
            if platform.system() == "Darwin":
                # player = MediaPlayer("default:none", format="avfoundation", options=options)
                player = MediaPlayer("rtsp://192.168.0.196:8080/h264_ulaw.sdp") # , options=options)
            else:
                player = MediaPlayer("/dev/video0", format="v4l2", options=options)

            await pc.setRemoteDescription(offer)
            for t in pc.getTransceivers():
                if t.kind == "audio" and player.audio:
                    pc.addTrack(player.audio)
                elif t.kind == "video" and player.video:
                    pc.addTrack(player.video)

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            # return web.Response(
            #     content_type="application/json",
            #     text=json.dumps(
            #         {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            #     ),
            # )
            print('SENDING ANSWER...')
            await self.socket.emit('answer', {
                'camera_id': params['camera_id'],
                'token': params['token'],
                'answer': {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            })

        @self.socket.on('registered')
        async def registered(data):
            print(data)

        @self.socket.on('disconnect')
        async def on_shutdown():
            # close peer connections
            coros = [pc.close() for pc in self.pcs]
            await asyncio.gather(*coros)
            self.pcs.clear()

    async def register(self):
        print(f'Registering: {self.user_id}')
        await self.socket.emit('register', {
            'user_id': self.user_id,
            'client_type': 'producer',
            'data': {}
        })

    async def make_view_available(self):
        print(f'Making view Available: {self.camera_id}')
        await self.socket.emit('make-available', {
            'camera_id': self.camera_id,
            'camera': {}
        })
