import sys
import time
import random
from user import Producer, Consumer

# producer testID
# consumer testID 1 2 3 4
user_type = sys.argv[1]
user_id = sys.argv[2]

print('User Type : ', user_type)
print('User ID : ', user_id)

if user_type == 'producer':
    client = Producer(user_id)
    while True:
        cams = client.camera_list
        for index in range(len(cams)):
            client.produce(cams[index], str(random.getrandbits(128)))
        time.sleep(1 / 15)

elif user_type == 'consumer':
    cams = []
    index = 3
    while index < len(sys.argv):
        cams.append(sys.argv[index])
        index += 1
    print('Cameras : ', cams)
    time.sleep(1)
    client = Consumer(user_id)
    time.sleep(1)
    client.set_cameras(cams)
