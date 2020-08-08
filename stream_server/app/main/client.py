import random

class ClientHandler:
    def __init__(self, session_id, user_id, socket):
        self.id = ClientHandler.generate_id(self)
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
    def __init__(self, session_id, user_id, socket, producer_id):
        super(Producer, self).__init__(session_id, user_id, socket)
        self.ids = []
        self.consumers = {}
        self.buffer = None
        self.active = False
        self.producer_id = producer_id

    # Send signal to producer to activate its broadcast
    def activate(self):
        if len(self.consumers) > 0 and len(self.ids) > 0:
            self.active = True
            self.socket.emit('activate-broadcast', {
                'user_id': self.user_id,
                'camera_list': self.ids
            }, room=self.session_id)
        elif len(self.consumers) == 0:
            self.deactivate()

    # Send signal to producer to deactivate its broadcast
    def deactivate(self):
        if len(self.consumers) == 0:
            self.active = False
            self.socket.emit('deactivate-broadcast', {
                'user_id': self.user_id
            }, room=self.session_id)
        elif len(self.consumers) > 0:
            self.activate()

    def add_consumer(self, consumer):
        self.consumers[consumer.id] = consumer

    def remove_consumer(self, id):
        del self.consumers[id]

    # Add Camera ID to Producer
    def add_id(self, id):
        if id not in self.ids:
            self.ids.append(id)
            self.activate()

    # Accept broacasted frame
    def produce(self, camera_id, frame):
        self.buffer = frame
        for client_id, consumer in self.consumers.items():
            if consumer is not None:
                consumer.consume(camera_id)

    def clean_ids(self):
        self.ids = []
        for client_id, consumer in self.consumers.items():
            if consumer is None:
                del self.consumers[client_id]
            else:
                for id in consumer.ids:
                    if id not in self.ids:
                        self.ids.append(id)
        if len(self.ids) > 0:
            self.activate()
        else:
            self.deactivate()

    def get_type(self):
        return 'producer'

class Consumer(ClientHandler):
    def __init__(self, session_id, user_id, socket):
        super(Consumer, self).__init__(session_id, user_id, socket)
        self.producer = None
        self.producer_id = None
        self.ids = []

    # Assign producer to consumer; Occurs when Receiving Camera List
    def set_producer(self, producer):
        self.producer_id = producer.producer_id
        # remove self from old producer
        if self.producer is not None:
            self.producer.remove_consumer(self.id)
        # set new producer
        self.producer = producer
        self.producer.add_consumer(self)

    def check_producer(self, producer_id):
        if self.producer is not None:
            if self.producer.producer_id == producer_id:
                return True
        return False

    # Add Camera IDs to Consumer
    def set_ids(self, camera_ids):
        self.clear_ids()
        for camera_id in camera_ids:
            self.ids.append(camera_id)
            if self.producer is not None:
                self.producer.add_id(camera_id)

    def clear_ids(self):
        self.ids = []
        if self.producer is not None:
            self.producer.clean_ids()

    # Consumer from the Producers Buffer
    def consume(self, camera_id):
        if self.producer is not None and camera_id in self.ids:
            frame = self.producer.buffer
            # emit frame bytecode to this client
            self.socket.emit('consume-frame', {
                'camera_id': camera_id,
                'frame': frame
            }, room=self.session_id)

    def get_type(self):
        return 'consumer'
