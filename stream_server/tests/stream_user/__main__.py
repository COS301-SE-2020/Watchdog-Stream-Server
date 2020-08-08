import sys
import time
import random
from user import Producer, Consumer

# producer testID prodID
# consumer testID prodID 1 2 3 4

user_type = sys.argv[1]
user_id = sys.argv[2]
producer_id = sys.argv[3]

print('User Type : ', user_type)
print('User ID : ', user_id)
print('Producer : ', producer_id)

if user_type == 'consumer':
    cams = []
    index = 4
    while index < len(sys.argv):
        cams.append(sys.argv[index])
        index += 1

    print('Cameras : ', cams)
    client = Consumer(user_id)
    client.set_cameras(producer_id, cams)

elif user_type == 'producer':
    client = Producer(user_id, producer_id)
    while True:
        cams = client.camera_list
        for index in range(len(cams)):
            client.produce(cams[index], str(random.getrandbits(128)))
        time.sleep(1 / 15)
