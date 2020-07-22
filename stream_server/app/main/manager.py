import time
from .client import Producer, Consumer


class ClientManager:
    def __init__(self, socket):
        # One-to-Many Producer-to-Consumer Relationship
        self.socket = socket
        self.producers = {}
        self.consumers = {}

    def authenticate_user(self, session_id, environ):
        # Expected { user_id, client_type, client_key }
        # Connect to Dynamo DB, check the user_id and client_key is valid - Client Key's Should be generated at API
        user_id = environ['user_id']
        client_type = environ['client_type']
        client_key = environ['client_key']

        print('Authenticating User: \n\
                User ID : ' + str(user_id) + '\n\
                Client Type : ' + str(client_type) + '\n\
                Client Key : ' + str(client_key) + '\n')

        client = None
        if client_type == 'producer':
            client = self.add_producer(session_id, user_id)
        elif client_type == 'consumer':
            client = self.add_consumer(session_id, user_id)
        else:
            print('User authentication failed...')
        self.check_connections()
        return client

    def remove_client(self, id, user_id):
        if self.producers[user_id].id == id:
            del self.producers[user_id]
        else:
            for index in range(len(self.consumers[user_id])):
                if self.consumers[user_id][index].id == id:
                    del self.consumers[user_id][index]
        self.clean_connections()

    def add_producer(self, session_id, user_id):
        if user_id in self.producers:
            print('Producer being overrode!')
            self.producers[user_id].deactivate()
            self.remove_client(self.producers[user_id].id, user_id)

        producer = Producer(session_id, user_id, self.socket)
        self.producers[user_id] = producer
        return producer

    def add_consumer(self, session_id, user_id):
        if user_id not in self.consumers:
            self.consumers[user_id] = []

        consumer = Consumer(session_id, user_id, self.socket)

        tries = 0
        while user_id not in self.producers:
            time.sleep(5)
            tries += 1
            if tries > 100:
                break

        if user_id in self.producers:
            consumer.set_producer(self.producers[user_id])
        else:
            print('Error: Producer not present!')
            return None

        self.consumers[user_id].append(consumer)
        return consumer

    def put_frame(self, user_id, frame):
        if user_id in self.producers:
            self.producers[user_id].produce(frame)
            self.retrieve_frames(user_id)

    def retrieve_frames(self, user_id):
        for index in range(len(self.consumers[user_id])):
            self.consumers[user_id][index].consume()

    def check_connections(self):
        for user_id, producer in self.producers.items():
            if user_id in self.consumers and len(self.consumers[user_id]) > 0:
                producer.activate()

    def clean_connections(self):
        for user_id, producer in self.producers.items():
            if len(self.consumers[user_id]) == 0:
                producer.deactivate()

    def __str__(self):
        to_string = ''
        for user_id, producer in self.producers.items():
            to_string += 'User : ' + str(user_id) + '\n'
            to_string += 'Producer : ' + str(producer.id) + '\n'
            if user_id in self.consumers:
                for index in range(len(self.consumers[user_id])):
                    to_string += '\tConsumer : ' + str(self.consumers[user_id][index].id) + '\n'
        return to_string
