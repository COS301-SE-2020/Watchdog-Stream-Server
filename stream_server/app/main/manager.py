import time
import threading
from .client import Producer, Consumer, TIMEOUT


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
        # Map of Missing Producer IDs to Consumer Session IDs
        self.requested = {}

    def run(self):
        while True:
            start = time.time()
            self.purge_old()
            diff = time.time() - start
            time.sleep(min(TIMEOUT, diff))

    def purge_old(self):
        clients = list(self.clients.keys())
        for session_id in clients:
            if not self.clients[session_id].is_active():
                self.remove_client(session_id)

    def register(self, session_id):
        if session_id in self.clients:
            self.clients[session_id].pulse()
        return session_id

    # authenticate a new client
    def authenticate_user(self, session_id, environ):
        client = None
        if 'user_id' not in environ or 'client_type' not in environ or 'client_key' not in environ:
            print('User authentication failed...')
            return client

        if session_id in self.clients:
            self.remove_client(session_id)

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
        # if this is the first producer for this user, account for it
        if user_id not in self.producers:
            self.producers[user_id] = {}

        if session_id in self.producers[user_id]:
            if self.producers[user_id][session_id].producer_id != producer_id:
                self.remove_client(session_id)

        if session_id in self.producers[user_id]:
            producer = self.producers[user_id][session_id]
            producer.set_available(available_cameras)
        else:
            producer = Producer(self.socket, session_id, user_id, producer_id, available_cameras)

        if producer is not None:
            self.producers[user_id][producer.session_id] = producer
            # check if any consumer might be trying to view this producer
            if producer_id in self.requested:
                if self.requested[producer_id] in self.consumers[user_id]:
                    consumer = self.consumers[user_id][self.requested[producer_id]]
                    consumer.set_producer(producer)
                    self.send_available_cameras(consumer.session_id, consumer.user_id)
                del self.requested[producer_id]
        return producer

    # add consumer client
    def add_consumer(self, session_id, user_id):
        if user_id not in self.consumers:
            self.consumers[user_id] = {}

        # producers = None
        if session_id in self.consumers[user_id]:
            # producers = self.consumers[user_id][session_id].producers.items()
            self.remove_client(session_id)

        consumer = Consumer(self.socket, session_id, user_id)

        if consumer is not None:
            # if producers is not None:
            #     for prod_id, prod in producers:
            #         consumer.set_producer(prod)
            self.consumers[user_id][consumer.session_id] = consumer
            self.send_available_cameras(session_id, user_id)

        return consumer

    # removes a client and detaches its connection
    def remove_client(self, session_id):
        if session_id in self.clients:
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
            print('Client disconnected...', session_id)

    # emits dictionary of producer_id : available camera list
    def send_available_cameras(self, session_id, user_id):
        available_producers = {}
        if user_id in self.producers:
            for producer_session_id, producer in self.producers[user_id].items():
                available_producers[producer.producer_id] = producer.get_available_ids()

        self.socket.emit('available-views', {
            'producers': available_producers
        }, room=session_id)

    # sets the cameras for a given client
    def set_cameras(self, session_id, producers):
        if session_id in self.clients:
            client = self.clients[session_id]
            for producer_id, camera_list in producers.items():
                if client.get_type() == 'consumer':
                    if not client.check_producer(producer_id):
                        if producer_id in Producer.producers:
                            client.set_producer(Producer.producers[producer_id])
                        else:
                            print('Warning: Requested Producer not present!')
                            self.requested[producer_id] = session_id
                    client.set_cameras(producer_id, camera_list)

    def put_frame(self, session_id, camera_id, frame):
        if session_id in self.clients:
            user_id = self.clients[session_id].user_id
            if user_id in self.producers:
                self.producers[user_id][session_id].produce(camera_id, frame)
