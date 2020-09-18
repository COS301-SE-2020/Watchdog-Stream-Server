import socketio
import random
import urllib3

CLIENT_KEY = 'supersecure'
# URL = 'https://stream.watchdog.thematthew.me:443/'
URL = 'http://127.0.0.1:5555'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Front-End Client Asbtract Class
class User:
    def __init__(self, user_id):
        self.id = self.generate_id(self)
        self.user_id = user_id
        self.socket = socketio.Client(ssl_verify=False)
        self.socket.connect(URL)

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

        # Data : { user_id : string, frame : string }
        @self.socket.on('consume-frame')
        def consume_frame(data):
            print('\tEVENT : consuming frame ... ', data)
            image = data['frame']
            self.consume(image)

        @self.socket.on('available-views')
        def available_views(data):
            print('\tEVENT : available views ... ', data)
            # probably want to activate all available streams
            # for producer_id, camera_ids in data['producers'].items():
            #     self.set_cameras(producer_id, camera_ids)
            #     break

    @staticmethod
    def generate_id(user):
        id = 'u' + str(random.getrandbits(128))
        return id


# Front-End Producer Client
class Producer(User):
    def __init__(self, user_id, producer_id, available_cameras):
        super(Producer, self).__init__(user_id)
        self.active = False
        self.camera_list = []
        self.send_count = 0
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
            self.socket.emit('produce-frame', {'camera_id': camera_id, 'frame': frame})
        self.send_count = self.send_count + 1

    def get_list(self):
        return self.camera_list

# Front-End Consumer Client
class Consumer(User):
    def __init__(self, user_id):
        super(Consumer, self).__init__(user_id)
        self.buffer = None
        self.producer_id = None
        self.camera_list = []
        self.receive_count = 0
        self.socket.emit('authorize', {'user_id': self.user_id, 'client_type': 'consumer', 'client_key': CLIENT_KEY})

    def set_cameras(self, producer_id=None, camera_list=[]):
        if producer_id is not None:
            self.producer_id = producer_id
        self.camera_list.extend(x for x in camera_list if x not in self.camera_list)
        if self.producer_id is not None:
            self.socket.emit('consume-view', {'producer_id': self.producer_id, 'camera_list': self.camera_list})

    # Mobile Client Consumer Draws frame data to screen
    def consume(self, data):
        self.buffer = data
        self.receive_count = self.receive_count + 1
