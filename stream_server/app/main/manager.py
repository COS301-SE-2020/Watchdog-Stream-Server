# import asyncio
from .client import Producer, Consumer


class ClientManager():
    def __init__(self, socket):
        # One-to-Many Producer-to-Consumer Relationship
        self.socket = socket
        # References to Producer & Consumer Objects indexed by session_id
        self.clients = {}
        # Producer Objects indexed by user_id and client_id
        self.producers = {}
        # Consumer Objects indexed by user_id and client_id
        self.consumers = {}

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
            if 'producer_id' in environ:
                producer_id = str(environ['producer_id'])
                available_cameras = []
                if 'available_cameras' in environ:
                    available_cameras = environ['available_cameras']
                client = self.add_producer(session_id, user_id, producer_id, available_cameras)
            else:
                print('Error: Missing Producer ID.')

        elif client_type == 'consumer':
            client = self.add_consumer(session_id, user_id)

        if client is not None:
            self.clients[session_id] = client

        return client

    def add_producer(self, session_id, user_id, producer_id, available_cameras):
        if user_id not in self.producers:
            self.producers[user_id] = {}

        producer = Producer(self.socket, session_id, user_id, producer_id, available_cameras)

        if producer is not None:
            self.producers[user_id][producer.id] = producer
            if user_id in self.consumers:
                for client_id, consumer in self.consumers[user_id].items():
                    if consumer.producer_id == producer_id and consumer.check_producer(producer_id) is False:
                        consumer.set_producer(producer)
                        self.send_available_cameras(consumer.session_id, consumer.user_id)

        return producer

    def add_consumer(self, session_id, user_id):
        if user_id not in self.consumers:
            self.consumers[user_id] = {}

        consumer = Consumer(self.socket, session_id, user_id)

        if consumer is not None:
            self.consumers[user_id][consumer.id] = consumer
            self.send_available_cameras(session_id, user_id)

        return consumer

    def remove_client(self, session_id):
        if session_id in self.clients:
            client = self.clients[session_id]
            client_id = client.id
            user_id = client.user_id

            # Remove it if its a Consumer
            if user_id in self.consumers:
                if client_id in self.consumers[user_id]:
                    self.consumers[user_id][client_id].clear_ids()
                    self.consumers[user_id][client_id] = None
                    del self.consumers[user_id][client_id]

            # Remove it if its a Producer
            if user_id in self.producers:
                if client_id in self.producers[user_id]:
                    self.producers[user_id][client_id] = None
                    del self.producers[user_id][client_id]

            self.clients[session_id] = None
            del self.clients[session_id]
            print('Client disconnected...') 

    def send_available_cameras(self, session_id, user_id):
        available_producers = {}
        if user_id in self.producers:
            for client_id, producer in self.producers[user_id].items():
                available_producers[producer.producer_id] = producer.get_available_ids()

        self.socket.emit('available-views', {
            'producers': available_producers
        }, room=session_id)

    def set_cameras(self, session_id, producer_id, camera_ids):
        if session_id in self.clients:
            client = self.clients[session_id]

            producing = False
            if client.check_producer(producer_id):
                producing = True
            elif client.get_type() == 'consumer':
                client.producer_id = producer_id
                if client.user_id in self.producers:
                    for client_id, producer in self.producers[client.user_id].items():
                        if producer.producer_id == producer_id:
                            producing = True
                            client.set_producer(producer)
                            break
            else:
                print('Warning: A non-consumer client is attempting to set cameras!')

            if not producing:
                print('Warning: Producer not present!')

            client.set_ids(camera_ids)

    def put_frame(self, session_id, camera_id, frame):
        if session_id in self.clients:
            client_id = self.clients[session_id].id
            user_id = self.clients[session_id].user_id
            if user_id in self.producers:
                self.producers[user_id][client_id].produce(camera_id, frame)

    def __str__(self):
        to_string = ''
        for user_id, producer in self.producers.items():
            to_string += 'User : ' + str(user_id) + '\n'
            to_string += 'Producer : ' + str(producer.id) + '\n'
            if user_id in self.consumers:
                for index in range(len(self.consumers[user_id])):
                    to_string += '\tConsumer : ' + str(self.consumers[user_id][index].id) + '\n'
        return to_string
