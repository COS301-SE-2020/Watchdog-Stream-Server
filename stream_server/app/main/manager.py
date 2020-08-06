import time
from threading import Thread, Lock
from .client import Producer, Consumer


class ClientManager(Thread):
    lock = Lock()

    def __init__(self, socket):
        # One-to-Many Producer-to-Consumer Relationship
        Thread.__init__(self)
        self.socket = socket
        self.clients = {}
        self.producers = {}
        self.consumers = {}

    def run(self):
        while True:
            self.check_connections()
            self.clean_connections()
            time.sleep(60)

    def authenticate_user(self, session_id, environ):
        # Connect to Dynamo DB, check the user_id and client_key is valid - Client Key's Should be generated at API
        user_id = str(environ['user_id'])
        client_type = str(environ['client_type'])
        client_key = str(environ['client_key'])

        print('Authenticating User: \n\
                \t\tUser ID : ' + user_id + '\n\
                \t\tClient Type : ' + client_type + '\n\
                \t\tClient Key : ' + client_key + '\n')

        client = None

        self.check_connections()

        if client_type == 'producer':
            client = self.add_producer(session_id, user_id)

        elif client_type == 'consumer':
            client = self.add_consumer(session_id, user_id)

        else:
            print('User authentication failed...')

        if client is not None:
            self.clients[client.id] = client
            self.check_connections()

        return client

    def add_producer(self, session_id, user_id):
        self.lock.acquire()

        if user_id in self.producers:
            print('Producer being overrode!')
            self.producers[user_id].deactivate()
            self.remove_client(self.producers[user_id].id)

        producer = Producer(session_id, user_id, self.socket)
        self.producers[user_id] = producer
        self.lock.release()
        return producer

    def add_consumer(self, session_id, user_id):
        self.lock.acquire()

        if user_id not in self.consumers:
            self.consumers[user_id] = []

        consumer = Consumer(session_id, user_id, self.socket)

        if user_id in self.producers:
            consumer.set_producer(self.producers[user_id])
        else:
            print('Warning: Producer not present!')

        self.consumers[user_id].append(consumer)

        self.lock.release()

        return consumer

    def remove_client(self, client_id):
        self.lock.acquire()
        if client_id in self.clients:
            user_id = self.clients[client_id].user_id
            if user_id in self.consumers:
                for index in range(len(self.consumers[user_id])):
                    if self.consumers[user_id][index].id == id:
                        self.consumers[user_id][index].clear_ids()
                        del self.consumers[user_id][index]
            if user_id in self.producers and self.producers[user_id].id == client_id:
                del self.producers[user_id]
            del self.clients[client_id]
        self.lock.release()
        self.clean_connections()

    def set_cameras(self, client_id, camera_ids):
        self.lock.acquire()

        if client_id in self.clients:
            for camera_id in camera_ids:
                self.clients[client_id].add_id(camera_id)

        self.lock.release()

    def put_frame(self, user_id, camera_id, frame):
        if user_id in self.producers:
            self.producers[user_id].produce(camera_id, frame)

    def check_connections(self):
        self.lock.acquire()
        for user_id, producer in self.producers.items():
            if user_id in self.consumers and len(self.consumers[user_id]) > 0:
                for consumer in self.consumers[user_id]:
                    if consumer.producer is None:
                        consumer.set_producer(self.producers[user_id])
                producer.activate()
        self.lock.release()

    def clean_connections(self):
        self.lock.acquire()
        for user_id, producer in self.producers.items():
            if user_id in self.consumers and len(self.consumers[user_id]) == 0:
                producer.clean()
                producer.deactivate()
        self.lock.release()

    def __str__(self):
        to_string = ''
        for user_id, producer in self.producers.items():
            to_string += 'User : ' + str(user_id) + '\n'
            to_string += 'Producer : ' + str(producer.id) + '\n'
            if user_id in self.consumers:
                for index in range(len(self.consumers[user_id])):
                    to_string += '\tConsumer : ' + str(self.consumers[user_id][index].id) + '\n'
        return to_string
