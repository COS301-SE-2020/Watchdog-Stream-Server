import time
from connection import socket_client
from user import Producer, Consumer

socket_client.connect('http://127.0.0.1:8008')

producer1 = Producer(1, socket_client)

time.sleep(1)

consumer11 = Consumer(1, socket_client)
time.sleep(1)
consumer12 = Consumer(1, socket_client)
time.sleep(1)
consumer13 = Consumer(1, socket_client)

time.sleep(1)

# producer2 = Producer(1, socket_client)

time.sleep(1)

consumer21 = Consumer(1, socket_client)
time.sleep(1)
consumer22 = Consumer(1, socket_client)

time.sleep(1)

while True:
    producer1.produce('xxx')
    time.sleep(1)
    producer1.produce('yyy')
    time.sleep(10)
