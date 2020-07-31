import random

class ClientHandler:
    def __init__(self, session_id, user_id, socket):
        self.id = ClientHandler.generate_id(self)
        self.user_id = user_id
        self.session_id = session_id
        self.socket = socket

    @staticmethod
    def generate_id(client):
        id = 'c' + str(random.getrandbits(128))
        return id


class Producer(ClientHandler):
    def __init__(self, session_id, user_id, socket):
        super(Producer, self).__init__(session_id, user_id, socket)
        self.buffer = None
        self.active = False
        self.ids = []
        self.consumers = {}

    # Send signal to producer to activate its broadcast
    def activate(self):
        if len(self.ids) > 0:
            self.active = True
            print('$$$$$$$ ACTIVATING CLIENT ', self.id, self.user_id, self.session_id)
            self.socket.emit('activate-broadcast', {
                'user_id': self.user_id,
                'camera_list': self.ids
            }, room=self.session_id)

    # Send signal to producer to deactivate its broadcast
    def deactivate(self):
        if len(self.ids) == 0:
            print('$$$$$$$ DEACTIVATING CLIENT ', self.id, self.user_id, self.session_id)
            self.active = False
            self.socket.emit('deactivate-broadcast', {
                'user_id': self.user_id,
                'camera_list': self.ids
            }, room=self.session_id)

    def add_consumer(self, consumer):
        print('$$$$$$$ ADDING CONSUMER TO PRODUCER ', self.id, self.user_id, self.session_id)
        self.consumers[consumer.id] = consumer

    # Add Camera ID to Producer
    def add_id(self, id):
        if id not in self.ids:
            print('$$$$$$$ ADDING camera id TO PRODUCER ', self.id, self.user_id, self.session_id)
            self.ids.append(id)
            self.activate()

    # Remove Camera ID from Producer
    def remove_id(self, id):
        if id in self.ids:
            print('$$$$$$$ REMOVING camera id FROM PRODUCER ', self.id, self.user_id, self.session_id)
            self.ids.remove(id)
            self.deactivate()

    # Accept broacasted frame
    def produce(self, camera_id, frame):
        print("$$$$$$$|-----|PRODUCING|-----|", camera_id, "|-----|", frame, "|-----|")
        self.buffer = frame
        for client_id, consumer in self.consumers.items():
            if consumer is not None:
                consumer.consume(camera_id)

    def clean(self):
        print('$$$$$$$ CLEANING camera id FROM PRODUCER ', self.id, self.user_id, self.session_id)
        for client_id, consumer in self.consumers.items():
            if consumer is None:
                del self.consumers[client_id]


class Consumer(ClientHandler):
    def __init__(self, session_id, user_id, socket):
        super(Consumer, self).__init__(session_id, user_id, socket)
        self.producer = None
        self.ids = []

    # Assign producer to consumer
    def set_producer(self, producer):
        print('$$$$$$$ SETTING PRODUCER ', self.id, ' => ', producer.id)
        self.producer = producer
        self.producer.add_consumer(self)
        for id in self.ids:
            self.producer.add_id(id)

    # Add Camera ID to Consumer
    def add_id(self, id):
        print('$$$$$$$ ADDING camera id TO CONSUMER ', self.id, self.user_id, self.session_id)
        if id not in self.ids:
            self.ids.append(id)
            if self.producer is not None:
                self.producer.add_id(id)

    # Remove Camera ID from Consumer
    def remove_id(self, id):
        print('$$$$$$$ REMOVING camera id FROM CONSUMER ', self.id, self.user_id, self.session_id)
        if id in self.ids:
            self.ids.remove(id)
            if self.producer is not None:
                self.producer.remove_id(id)

    def clear_ids(self):
        print('$$$$$$$ CLEARING camera id FROM CONSUMER ', self.id, self.user_id, self.session_id)
        for id in self.ids:
            self.remove_id(id)

    # Consumer from the Producers Buffer
    def consume(self, camera_id):
        print("$$$$$$$|-----|CONSUMING|-----|", camera_id, "|-----|")
        if self.producer is not None and camera_id in self.ids:
            frame = self.producer.buffer
            # emit frame bytecode to this client
            self.socket.emit('consume-frame', {
                'user_id': self.user_id,
                'frame': frame
            }, room=self.session_id)
