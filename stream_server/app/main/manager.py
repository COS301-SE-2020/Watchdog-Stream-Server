# import asyncio
from .client import Producer, Consumer


class ClientManager():
    def __init__(self, socket):
        # One-to-Many Producer-to-Consumer Relationship
        self.socket = socket
        self.clients = {}
        self.producers = {}
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
        elif client_type == 'consumer':
            client = self.add_consumer(session_id, user_id)

        if client is not None:
            self.clients[client.id] = client

        return client

    def add_producer(self, session_id, user_id, producer_id, available_cameras):
        if user_id not in self.producers:
            self.producers[user_id] = {}

        producer = Producer(self.socket, session_id, user_id, producer_id, available_cameras)

        if producer.id in self.producers[user_id]:
            print('Warning: Overwriting producer with matching ID...')

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
        for client_id, client in self.clients.items():
            if session_id == client.session_id:
                user_id = client.user_id

                if user_id in self.consumers:
                    if client_id in self.consumers[user_id]:
                        self.consumers[user_id][client_id].clear_ids()
                        self.consumers[user_id][client_id] = None
                        del self.consumers[user_id][client_id]

                if user_id in self.producers:
                    if client_id in self.producers[user_id]:
                        self.producers[user_id][client_id] = None
                        del self.producers[user_id][client_id]

                self.clients[client_id] = None
                del self.clients[client_id]
                print('Client disconnected...')
                break

    def send_available_cameras(self, session_id, user_id):
        available_producers = {}
        if user_id in self.producers:
            for client_id, producer in self.producers[user_id].items():
                available_producers[producer.producer_id] = producer.get_available_ids()

        self.socket.emit('available-views', {
            'producers': available_producers
        }, room=session_id)

    def set_cameras(self, client_id, producer_id, camera_ids):
        if client_id in self.clients:
            client = self.clients[client_id]

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

    async def put_frame(self, user_id, client_id, camera_id, frame):
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
