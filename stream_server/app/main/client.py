import random


class ClientHandler:
    def __init__(self, session_id, user_id, socket):
        # self.id = ClientHandler.generate_id(self)
        self.id = user_id + session_id
        self.user_id = user_id
        self.session_id = session_id
        self.socket = socket

    def get_type(self):
        return ''

    @staticmethod
    def generate_id(client):
        id = 'c' + str(random.getrandbits(128))
        return id


class Producer(ClientHandler):
    def __init__(self, socket, session_id, user_id, producer_id, available_camera_ids=[]):
        super(Producer, self).__init__(session_id, user_id, socket)
        self.producer_id = producer_id
        self.available_camera_ids = available_camera_ids
        self.requested_camera_ids = []
        self.consumers = {}
        self.active = False
        self.buffer = None

    # Send signal to producer to activate its broadcast
    def activate(self):
        camera_ids = [cam_id for cam_id in self.requested_camera_ids if cam_id in self.available_camera_ids]
        if len(self.consumers) > 0 and len(camera_ids) > 0:
            self.active = True
            self.socket.emit('activate-broadcast', {
                'user_id': self.user_id,
                'camera_list': camera_ids
            }, room=self.session_id)
        elif len(self.consumers) == 0:
            self.deactivate()

    # Send signal to producer to deactivate its broadcast
    def deactivate(self):
        if len(self.consumers) == 0 or len(self.requested_camera_ids) == 0:
            self.active = False
            self.socket.emit('deactivate-broadcast', {
                'user_id': self.user_id
            }, room=self.session_id)
        else:
            self.activate()

    # attach consumer
    def attach_consumer(self, consumer):
        self.consumers[consumer.id] = consumer
        if consumer.requested_camera_ids is not None:
            for camera_id in consumer.requested_camera_ids:
                self.add_camera(camera_id)

    # detach consumer
    def detach_consumer(self, consumer, clean_up=False):
        if consumer.id in self.consumers:
            if clean_up and consumer.requested_camera_ids is not None:
                # all ids of removed client
                unneeded = set(consumer.requested_camera_ids)
                # for every other client
                for client_id, needed_consumer in self.consumers.items():
                    if client_id != consumer.id:
                        # get this clients needed set of cameras
                        needed = set(needed_consumer.requested_camera_ids)
                        # removed all the needed ids from the unneeded set
                        unneeded = unneeded - needed
                        if len(unneeded) == 0:
                            break
                needed = set(self.requested_camera_ids)
                self.requested_camera_ids = list(needed - unneeded)
            self.consumers[consumer.id].set_producer(None)
            del self.consumers[consumer.id]
        if len(self.requested_camera_ids) == 0:
            self.deactivate()

    # detach consumers
    def detach_consumers(self):
        consumers = list(self.consumers.keys())
        for client_id in consumers:
            self.detach_consumer(self.consumers[client_id])

    # Add Camera ID to Producer
    def add_camera(self, id):
        if id not in self.requested_camera_ids:
            self.requested_camera_ids.append(id)
            self.activate()

    def get_available_ids(self):
        return self.available_camera_ids

    # Accept broacasted frame
    def produce(self, camera_id, frame):
        self.buffer = frame
        consumers = self.consumers.items()
        for client_id, consumer in consumers:
            if consumer is not None:
                consumer.consume(camera_id)

    def get_type(self):
        return 'producer'


class Consumer(ClientHandler):
    def __init__(self, socket, session_id, user_id):
        super(Consumer, self).__init__(session_id, user_id, socket)
        self.producer = None
        self.producer_id = None
        self.requested_camera_ids = []

    # Assign producer to consumer; Occurs when Receiving Camera List
    def set_producer(self, producer):
        # setting producer to null
        if producer is None:
            self.producer = None
            self.producer_id = None
        else:
            # remove self from old producer
            if self.producer is not None:
                self.producer.detach_consumer(self, True)
            # set new producer
            self.producer_id = producer.producer_id
            self.producer = producer
            self.producer.attach_consumer(self)

    def unset_producer(self):
        if self.producer is not None:
            self.producer.detach_consumer(self, True)
            self.producer = None
            self.producer_id = None

    # Check if the producer is assigned
    def check_producer(self, producer_id):
        if self.producer_id == producer_id:
            if self.producer is not None:
                if self.producer.producer_id == producer_id:
                    return True
            elif producer_id is None:
                return True
        return False

    # Add Camera IDs to Consumer
    def set_cameras(self, camera_ids):
        self.requested_camera_ids = []
        for camera_id in camera_ids:
            self.requested_camera_ids.append(camera_id)
            if self.producer is not None:
                self.producer.add_camera(camera_id)

    # Consumes from the Producers Buffer
    def consume(self, camera_id):
        if self.producer is not None and camera_id in self.requested_camera_ids:
            frame = self.producer.buffer
            # emit frame bytecode to this client
            self.socket.emit('consume-frame', {
                'camera_id': camera_id,
                'frame': frame
            }, room=self.session_id)

    def get_type(self):
        return 'consumer'
