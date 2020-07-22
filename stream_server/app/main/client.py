class Client:
    clients = {}

    def __init__(self, session_id, user_id, socket):
        self.id = Client.generate_id(self)
        self.user_id = user_id
        self.session_id = session_id
        self.socket = socket

    @staticmethod
    def generate_id(client):
        id = 'c' + str(len(Client.clients))
        Client.clients[id] = client
        return id


class Producer(Client):
    def __init__(self, session_id, user_id, socket):
        super(Producer, self).__init__(session_id, user_id, socket)
        self.buffer = None
        self.active = False

    # Send signal to producer to activate its broadcast
    def activate(self):
        self.socket.emit('broadcast', {'client_id': self.id, 'user_id': self.user_id, 'session_id': self.session_id, 'active': True}, room=self.session_id)

    # Send signal to producer to deactivate its broadcast
    def deactivate(self):
        self.socket.emit('broadcast', {'client_id': self.id, 'user_id': self.user_id, 'session_id': self.session_id, 'active': False}, room=self.session_id)

    # Accept broacasted frame
    def produce(self, frame):
        print('producing ', frame)
        self.buffer = frame

    # Read the buffer
    def read(self):
        return self.buffer


class Consumer(Client):
    def __init__(self, session_id, user_id, socket):
        super(Consumer, self).__init__(session_id, user_id, socket)
        self.producer = None

    # Assign producer to consumer
    def set_producer(self, producer):
        self.producer = producer

    # Consumer from the Producers Buffer
    def consume(self):
        if self.producer is not None:
            frame = self.producer.read()
            # emit frame bytecode to this client
            self.socket.emit('stream', {'client_id': self.id, 'user_id': self.user_id, 'session_id': self.session_id, 'frame': frame}, room=self.session_id)
