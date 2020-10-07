import time
import threading
from .client import Producer, Consumer, TIMEOUT
import asyncio

class ClientManager(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        # One-to-Many Producer-to-Consumer Relationship
        self.socket = socket
        # References to Producer & Consumer Objects indexed by session_id
        self.clients = {}
        # Producer Objects indexed by user_id and client_id
        self.producers = {}
        # Consumer Objects indexed by user_id and client_id
        self.consumers = {}

    def run(self):
        while True:
            start = time.time()
            self.purge()
            diff = time.time() - start
            time.sleep(TIMEOUT - diff)

    def purge(self):
        clients = list(self.clients.keys())
        for session_id in clients:
            if self.clients[session_id] is not None and not self.clients[session_id].is_active():
                self.remove_client(session_id)
        for user_id in self.producers.keys():
            for session_id, producer in self.producers[user_id].items():
                if producer.currently_producing:
                    producer.check_active()
                if not producer.is_active():
                    self.remove_client(session_id)
        for user_id in self.consumers.keys():
            for session_id, consumer in self.consumers[user_id].items():
                if not consumer.is_active():
                    self.remove_client(session_id)

    def pulse(self, session_id):
        if session_id in self.clients and self.clients[session_id] is not None:
            self.clients[session_id].pulse()
        return session_id

    # Make Provisions for a new Client Connection
    def connected(self, session_id):
        # If it Exists and is a Producer Remove it and its Connections
        if session_id in self.clients and self.clients[session_id].get_type() == 'producer':
            self.remove_client(session_id)
        # Consumers will have new (Potentially Duplicate) Connections Created and the old ones will be cleaned up
        self.clients[session_id] = None

    # Remove Client
    def disconnected(self, session_id):
        self.remove_client(session_id)

    # authenticate a new client
    def authenticate_user(self, session_id, environ):
        client = None
        if 'user_id' not in environ or 'client_type' not in environ or 'client_key' not in environ:
            print('User authentication failed...')
            return client

        # Connect to Dynamo DB, check the user_id and client_key is valid - Client Key's Should be generated at API
        client_key = str(environ['client_key'])
        # Get Client Type
        client_type = str(environ['client_type'])
        # Get User ID
        user_id = str(environ['user_id'])

        print('Authenticating User: \n\
                \t\tUser ID : ' + user_id + '\n\
                \t\tClient Type : ' + client_type + '\n\
                \t\tClient Key : ' + client_key + '\n')

        if client_type == 'producer':
            if 'producer_id' in environ and 'available_cameras' in environ:
                client = self.add_producer(session_id, user_id, str(environ['producer_id']), environ['available_cameras'])
            else:
                print('Error: Missing Producer ID.')

        elif client_type == 'consumer':
            client = self.add_consumer(session_id, user_id)

        if client is not None:
            self.clients[session_id] = client

        return client

    # add producer client
    def add_producer(self, session_id, user_id, producer_id, available_cameras):
        # Check if Already Connected
        if user_id in self.producers and session_id in self.producers[user_id]:
            self.pulse(session_id)
            self.producers[user_id][session_id].set_available(available_cameras)
            return self.producers[user_id][session_id]
        # Check if an Old Connection for this Producer ID is still Around
        elif producer_id in Producer.producers:
            print('Overriding Existing Producer Connection')
            self.remove_client(Producer.producers[producer_id].session_id)

        # if this is the first producer for this user, account for it
        if user_id not in self.producers:
            self.producers[user_id] = {}

        self.producers[user_id][session_id] = Producer(self.socket, session_id, user_id, producer_id, available_cameras)
        # check if any consumer might be trying to view this producer
        if user_id in self.consumers:
            for consumer_session_id, consumer in self.consumers[user_id].items():
                if self.producers[user_id][session_id].producer_id in consumer.requested_ids:
                    consumer.set_producer(self.producers[user_id][session_id])
                self.send_available_cameras(consumer_session_id, user_id)

        return self.producers[user_id][session_id]

    # add consumer client
    def add_consumer(self, session_id, user_id):
        if user_id in self.consumers and session_id in self.consumers[user_id]:
            self.pulse(session_id)
            self.send_available_cameras(session_id, user_id)
            return self.consumers[user_id][session_id]

        if user_id not in self.consumers:
            self.consumers[user_id] = {}

        self.consumers[user_id][session_id] = Consumer(self.socket, session_id, user_id)

        if self.consumers[user_id][session_id] is not None:
            self.send_available_cameras(session_id, user_id)

        return self.consumers[user_id][session_id]

    # removes a client and detaches its connection
    def remove_client(self, session_id):
        if session_id in self.clients and self.clients[session_id] is not None:
            client = self.clients[session_id]
            user_id = client.user_id

            self.clients[session_id] = None
            # Remove it if its a Consumer
            if user_id in self.consumers:
                if session_id in self.consumers[user_id]:
                    self.consumers[user_id][session_id].unset_producers()
                    del self.consumers[user_id][session_id]
            # Remove it if its a Producer
            if user_id in self.producers:
                if session_id in self.producers[user_id]:
                    self.producers[user_id][session_id].detach_consumers()
                    del self.producers[user_id][session_id]
            del self.clients[session_id]
        else:  # Remove any remaining references if has been overwritten
            for user_id in self.producers.keys():
                if session_id in self.producers[user_id]:
                    self.producers[user_id][session_id].detach_consumers()
                    del self.producers[user_id][session_id]
            for user_id in self.consumers.keys():
                if session_id in self.consumers[user_id]:
                    self.consumers[user_id][session_id].unset_producers()
                    del self.consumers[user_id][session_id]
        print('Client disconnected...', session_id)

    # emits dictionary of producer_id : available camera list
    def send_available_cameras(self, session_id, user_id=None):
        if user_id is None:
            if session_id in self.clients and self.clients[session_id] is not None:
                user_id = self.clients[session_id].user_id
            else:
                return
        self.pulse(session_id)
        available_producers = {}
        if user_id in self.producers:
            producer_session_ids = self.producers[user_id].keys()
            for producer_session_id in producer_session_ids:
                if producer_session_id in self.producers[user_id]:
                    available_producers[self.producers[user_id][producer_session_id].producer_id] = self.producers[user_id][producer_session_id].get_available_ids()
        self.socket.emit('available-views', {
            'producers': available_producers
        }, room=session_id)

    # sets the cameras for a given client
    def set_cameras(self, session_id, producers):
        self.pulse(session_id)
        if session_id in self.clients and self.clients[session_id] is not None:
            client = self.clients[session_id]  # consumer
            if client.get_type() == 'consumer':
                for producer_id, camera_list in producers.items():
                    client.set_cameras(producer_id, camera_list)
                    if not client.check_producer(producer_id):
                        if producer_id in Producer.producers:
                            client.set_producer(Producer.producers[producer_id])
                        else:
                            print('Warning: Requested Producer not present!')
            self.send_available_cameras(session_id, client.user_id)

    # sends sdp & type to each specified producer
    # def connect_camera(self, session_id, camera_id, rtc_sdp, rtc_type):
    #     print('Connecting Camera', session_id, camera_id)
    #     if session_id in self.clients and self.clients[session_id] is not None:
    #         user_id = self.clients[session_id].user_id
    #         if user_id in self.producers:
    #             for producer_session_id, producer in self.producers[user_id].items():
    #                 if camera_id in producer.available_ids:
    #                     print('SENDING Connecting Camera', session_id, camera_id)
    #                     self.socket.emit('connect-rtc', {'connection': {
    #                         'sdp': rtc_sdp,
    #                         'type': rtc_type,
    #                         'camera_id': camera_id,
    #                         'peer_session_id': session_id
    #                     }}, room=producer_session_id)

    def connect_camera(self, camera_id, rtc_sdp, rtc_type, callback):
        print('Connecting Camera', camera_id)
        for user_id in self.producers.keys():
            for session_id, producer in self.producers[user_id].items():
                if camera_id in producer.available_ids:
                    print('SENDING Connecting Camera', session_id, camera_id)
                    self.result = {}

                    def callback_func(r):
                        self.result = r
                        callback(self.result)

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(producer.offer({
                        'sdp': rtc_sdp,
                        'type': rtc_type,
                        'camera_id': camera_id,
                        'peer_session_id': session_id
                    }, callback_func))

                    return self.result

    def put_frame(self, session_id, camera_id, frame):
        if session_id in self.clients and self.clients[session_id] is not None:
            user_id = self.clients[session_id].user_id
            if user_id in self.producers:
                self.producers[user_id][session_id].produce(camera_id, frame)

    def print(self):
        print('Clients:\n\t', self.clients.keys())
        for user_id in self.producers.keys():
            for session_id, producer in self.producers[user_id].items():
                print('Producer', session_id, producer.producer_id)
                print('\tattached cons', session_id, producer.consumers.keys())
        for user_id in self.consumers.keys():
            for session_id, consumer in self.consumers[user_id].items():
                print('Consumer', session_id)
                print('\tattached prods', session_id, consumer.producers.keys())
