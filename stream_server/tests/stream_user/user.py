import socketio
import random

CLIENT_KEY = 'supersecure'
URL = 'http://ec2-13-245-35-130.af-south-1.compute.amazonaws.com:8080'

# Front-End Client Asbtract Class
class User:
    def __init__(self, user_id):
        self.id = self.generate_id(self)
        self.user_id = user_id
        self.socket = socketio.Client()
        self.socket.connect(URL)

        # Data : { user_id : string, camera_list : string }
        @self.socket.on('activate-broadcast')
        def activate_broadcast(data):
            print('activating broadcast ... ', data, self.id)
            self.activate(data['camera_list'])

        # Data : { user_id : string, camera_list : string }
        @self.socket.on('deactivate-broadcast')
        def deactivate_broadcast(data):
            print('deactivating broadcast ... ', data, self.id)
            self.deactivate()

        # Data : { user_id : string, frame : string }
        @self.socket.on('consume-frame')
        def consume_frame(data):
            print('consuming frame ... ', data, self.id)
            image = data['frame']
            self.consume(image)

    @staticmethod
    def generate_id(user):
        id = 'u' + str(random.getrandbits(128))
        return id


# Front-End Producer Client
class Producer(User):
    def __init__(self, user_id, producer_id):
        super(Producer, self).__init__(user_id)
        self.active = False
        self.camera_list = []
        self.socket.emit('authorize', {'user_id': self.user_id, 'client_type': 'producer', 'producer_id': producer_id, 'client_key': CLIENT_KEY})

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
            self.socket.emit('produce-frame', {'camera_id': camera_id, 'frame': frame})

    def get_list(self):
        return self.camera_list

# Front-End Consumer Client
class Consumer(User):
    def __init__(self, user_id):
        super(Consumer, self).__init__(user_id)
        self.buffer = None
        self.socket.emit('authorize', {'user_id': self.user_id, 'client_type': 'consumer', 'client_key': CLIENT_KEY})

    def set_cameras(self, producer_id, camera_list):
        self.socket.emit('consume-view', {'producer_id': producer_id, 'camera_list': camera_list})

    # Mobile Client Consumer Draws frame data to screen
    def consume(self, data):
        self.buffer = data
