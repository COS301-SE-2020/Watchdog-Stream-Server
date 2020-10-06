import time
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer


TIMEOUT = 600


class ClientHandler:
    def __init__(self, session_id, user_id, socket):
        self.user_id = user_id
        self.session_id = session_id
        self.socket = socket
        self.pulse()

    def pulse(self):
        self.last_seen = time.time()

    def is_active(self):
        if time.time() < self.last_seen + TIMEOUT:
            return True
        return False

    def get_type(self):
        return ''


class Producer(ClientHandler):
    producers = {}

    def __init__(self, socket, session_id, user_id, producer_id, available_ids=[]):
        super(Producer, self).__init__(session_id, user_id, socket)
        self.producer_id = producer_id
        self.available_ids = available_ids
        self.consumers = {}
        self.requested_ids = []
        self.currently_producing = False
        Producer.producers[self.producer_id] = self
        self.timer = time.time()

        self.pcs = {}

    def set_available(self, available_ids):
        self.available_ids = available_ids

    def check_active(self):
        if len(self.consumers) == 0 or len(self.requested_ids) == 0:
            self.deactivate()
        else:
            self.activate()

    # Send signal to producer to activate its broadcast
    def activate(self):
        self.pulse()
        camera_ids = [cam_id for cam_id in self.requested_ids if cam_id in self.available_ids]
        if len(camera_ids) > 0 and len(self.consumers) > 0:
            self.currently_producing = True
            self.socket.emit('activate-broadcast', {
                'user_id': self.user_id,
                'camera_list': camera_ids
            }, room=self.session_id)
        else:
            self.deactivate()

    # Send signal to producer to deactivate its broadcast
    def deactivate(self):
        self.pulse()
        camera_ids = [cam_id for cam_id in self.requested_ids if cam_id in self.available_ids]
        if len(camera_ids) == 0 or len(self.consumers) == 0:
            self.currently_producing = False
            self.socket.emit('deactivate-broadcast', {
                'user_id': self.user_id
            }, room=self.session_id)
        elif len(camera_ids) > 0 and len(self.consumers) > 0:
            self.activate()

    # attach consumer
    def attach_consumer(self, consumer):
        self.consumers[consumer.session_id] = consumer
        if consumer.requested_ids is not None:
            for camera_id in consumer.requested_ids:
                self.add_camera(camera_id)

    # detach consumer
    def detach_consumer(self, consumer, clean_up=False):
        if consumer.session_id in self.consumers:
            # Clean Up of Unnecessary Camera IDS
            if clean_up and consumer.requested_ids is not None:
                # all ids of removed client
                unneeded = set(consumer.requested_ids)
                # for every other client
                for client_id, needed_consumer in self.consumers.items():
                    if client_id != consumer.session_id:
                        # get this clients needed set of cameras
                        needed = set(needed_consumer.requested_ids)
                        # removed all the needed ids from the unneeded set
                        unneeded = unneeded - needed
                        if len(unneeded) == 0:
                            break
                needed = set(self.requested_ids)
                self.requested_ids = list(needed - unneeded)
            consumer = self.consumers[consumer.session_id]
            del self.consumers[consumer.session_id]
            if consumer.check_producer(self.producer_id):
                consumer.unset_producer(self, False)
        self.activate()

    # detach consumers, removing producer, kills producer essentially
    def detach_consumers(self):
        consumers = list(self.consumers.keys())
        for client_id in consumers:
            self.detach_consumer(self.consumers[client_id])
        del Producer.producers[self.producer_id]

    # Add Camera ID to Producer
    def add_camera(self, id):
        if id not in self.requested_ids:
            self.requested_ids.append(id)
            self.activate()

    def check_consumer(self, consumer_id):
        if consumer_id in self.consumers:
            return True
        return False

    def get_available_ids(self):
        return self.available_ids

    # Accept broacasted frame
    def produce(self, camera_id, frame):
        self.pulse()
        sent = False
        consumer_keys = self.consumers.keys()
        for client_id in consumer_keys:
            if client_id in self.consumers:
                outcome = self.consumers[client_id].consume(self.producer_id, camera_id, frame)
                if not outcome:
                    if self.consumers[client_id].check_producer(self.producer_id):
                        self.consumers[client_id].unset_producer(self)
                    self.detach_consumer(self.consumers[client_id])
                sent = sent or outcome
        if not sent:
            if camera_id in self.requested_ids:
                self.requested_ids.remove(camera_id)
            if len(self.requested_ids) == 0:
                self.deactivate()
        self.socket.sleep(max((1 / 60) - (time.time() - self.timer), 0))
        self.timer = time.time()

    def get_type(self):
        return 'producer'

    async def offer(self, request, callback):
        self.player = MediaPlayer("rtsp://10.0.0.109:8080/h264_ulaw.sdp")
        print('OFFER')
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

        # self.socket.emit('connected-rtc', {'camera_id': camera_id, 'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type}, room=peer_session_id)
        response = {'camera_id': camera_id, 'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type}
        callback(response)

class Consumer(ClientHandler):
    def __init__(self, socket, session_id, user_id):
        super(Consumer, self).__init__(session_id, user_id, socket)
        self.producers = {}
        self.requested_ids = {}

    # Assign producer to consumer; Occurs when Receiving Camera List
    def set_producer(self, producer):
        # Ensure it is the most recently created producer
        producer_id = producer.producer_id
        if producer.session_id != Producer.producers[producer_id].session_id:
            producer = Producer.producers[producer_id]
        # Check if somehow an old session is still attached
        if producer_id in self.producers and self.producers[producer_id].session_id != producer.session_id:
            if self.producers[producer_id].check_consumer(self.session_id):
                self.producers[producer_id].detach_consumer(self)
            del self.producers[producer_id]
        # Attach Producer
        self.producers[producer_id] = producer
        self.producers[producer_id].attach_consumer(self)
        if self.get_cameras(producer_id) is not None:
            for requested_id in self.requested_ids[producer_id]:
                producer.add_camera(requested_id)

    def unset_producer(self, producer, recur=True):
        if producer.producer_id in self.producers:
            del self.producers[producer.producer_id]
            if producer.check_consumer(self.session_id) and recur:
                producer.detach_consumer(self)

    def unset_producers(self):
        producers = list(self.producers.keys())
        for producer_id in producers:
            producer = self.producers[producer_id]
            del self.producers[producer_id]
            if producer.check_consumer(self.session_id):
                producer.detach_consumer(self, True)

    # Check if the producer is assigned
    def check_producer(self, producer_id):
        if producer_id in self.producers and self.producers[producer_id].session_id == Producer.producers[producer_id].session_id:
            return True
        return False

    # Check if the producer is assigned
    def get_cameras(self, producer_id):
        if producer_id in self.requested_ids:
            return self.requested_ids[producer_id]
        return None

    # Add Camera IDs to Consumer, Is checked by producers if recently come online
    def set_cameras(self, producer_id, camera_ids):
        self.requested_ids[producer_id] = []  # need to clear otherwise requests will just build up
        for camera_id in camera_ids:
            if camera_id not in self.requested_ids[producer_id]:
                self.requested_ids[producer_id].append(camera_id)
                if producer_id in self.producers:
                    self.producers[producer_id].add_camera(camera_id)
        producer_ids = self.requested_ids.keys()
        for producer_id in producer_ids:
            if not self.check_producer(producer_id):
                if producer_id in Producer.producers:
                    self.set_producer(Producer.producers[producer_id])

    # Consumes from the Producers Buffer
    def consume(self, producer_id, camera_id, frame):
        outcome = False
        if camera_id in self.requested_ids[producer_id]:
            outcome = True
            if producer_id in self.producers and self.producers[producer_id] is None:
                if producer_id in Producer.producers:
                    self.set_producer(Producer.producers[producer_id])
                else:
                    print('Warning: Producer Emitting to Client without Established Connection')
                    outcome = False
            self.socket.emit('consume-frame', {
                'camera_id': camera_id,
                'frame': frame
            }, room=self.session_id)
        if outcome:
            self.pulse()
        return outcome

    def get_type(self):
        return 'consumer'
