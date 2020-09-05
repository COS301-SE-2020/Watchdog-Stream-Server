import sys
import time
import random
from user import Producer, Consumer

# producer/consumer user_id prod_id cam_id1 cam_id2 cam_id3 cam_id4 ...

user_type = sys.argv[1]
user_id = sys.argv[2]
producer_id = sys.argv[3]
cams = []
for index in range(4, len(sys.argv)):
    cams.append(sys.argv[index])

print('User Type : ', user_type)
print('User ID : ', user_id)
print('Producer ID : ', producer_id)
print('Camera IDs : ', cams)

if user_type == 'consumer':
    print('Cameras : ', cams)
    client = Consumer(user_id)
    client.set_cameras(producer_id, cams)

elif user_type == 'producer':
    client = Producer(user_id, producer_id, cams)
    while True:
        cams = client.camera_list
        for index in range(len(cams)):
            client.produce(cams[index], str(random.getrandbits(128)))
        time.sleep(0.5)
