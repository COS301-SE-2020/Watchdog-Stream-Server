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

    # add producer client
    def add_producer(self, session_id, user_id, producer_id, available_cameras):
        # if this is the first producer for this user, account for it
        if user_id not in self.producers:
            self.producers[user_id] = {}

        producer = Producer(self.socket, session_id, user_id, producer_id, available_cameras)

        if producer is not None:
            self.producers[user_id][producer.id] = producer
            # check if any consumer might be trying to view this producer
            if user_id in self.consumers:
                for client_id, consumer in self.consumers[user_id].items():
                    if consumer.producer_id == producer_id:
                        if consumer.check_producer(None) or consumer.check_producer(producer_id) is False:
                            consumer.set_producer(producer)
                            self.send_available_cameras(consumer.session_id, consumer.user_id)

        return producer

    # add consumer client
    def add_consumer(self, session_id, user_id):
        if user_id not in self.consumers:
            self.consumers[user_id] = {}

        consumer = Consumer(self.socket, session_id, user_id)

        if consumer is not None:
            self.consumers[user_id][consumer.id] = consumer
            self.send_available_cameras(session_id, user_id)

        return consumer

    # removes a client and detaches its connection
    def remove_client(self, session_id):
        if session_id in self.clients:
            client = self.clients[session_id]
            client_id = client.id
            user_id = client.user_id

            # Remove it if its a Consumer
            if user_id in self.consumers:
                if client_id in self.consumers[user_id]:
                    self.consumers[user_id][client_id].unset_producer()
                    # Set to none so can be deleted from clients without error
                    self.consumers[user_id][client_id] = None
                    del self.consumers[user_id][client_id]

            # Remove it if its a Producer
            if user_id in self.producers:
                if client_id in self.producers[user_id]:
                    self.producers[user_id][client_id].detach_consumers()
                    # Set to none so can be deleted from clients without error
                    self.producers[user_id][client_id] = None
                    del self.producers[user_id][client_id]

            del self.clients[session_id]
            print('Client disconnected...') 

    # emits dictionary of producer_id : available camera list
    def send_available_cameras(self, session_id, user_id):
        available_producers = {}
        if user_id in self.producers:
            for client_id, producer in self.producers[user_id].items():
                available_producers[producer.producer_id] = producer.get_available_ids()

        self.socket.emit('available-views', {
            'producers': available_producers
        }, room=session_id)

    # sets the cameras for a given client
    def set_cameras(self, session_id, producer_id, camera_ids):
        if session_id in self.clients:
            client = self.clients[session_id]

            producing = False
            # checks if client has an assigned producer with the given id
            if client.check_producer(producer_id):
                producing = True
            # if producer not assigned, and it is a consumer, assign the given producer id
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

            client.set_cameras(camera_ids)

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
