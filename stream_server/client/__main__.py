import sys
import time
import datetime
import random
from user import Producer, Consumer

# producer user_id prod_id cam_id1 cam_id2 cam_id3 cam_id4 ...
# consumer user_id - prod_id1 cam_id1 cam_id2 - prod_id2 cam_id3 cam_id4 ...

user_type = sys.argv[1]
user_id = sys.argv[2]

time.sleep(random.randint(1, 10))

print('STARTING STREAM SERVER CLIENT TESTING ENVIRONMENT')
if user_type == 'consumer':
    producers = {}
    for index in range(3, len(sys.argv)):
        if sys.argv[index - 1] == '-':
            pindex = sys.argv[index]
            cameras = []
            for new_index in range(index + 1, len(sys.argv)):
                if sys.argv[new_index] == '-':
                    break
                cameras.append(sys.argv[new_index])
            producers[pindex] = cameras

    print('CONSTRUCTED CONSUMER CLIENT ENVIRONMENT')
    print('\tUSER-ID : ', user_id)
    print('\tPRODUCERS: ', producers)
    client = Consumer(user_id)
    client.set_cameras(producers)
    time.sleep(8)
    # time.sleep(165)
    print('CONSUMER RECEIVED [' + str(client.receive_count) + '] MESSAGES')
    print('CONSUMER PASSED REQUIRED PERFORANCE TESTING')
    time.sleep(10)
    client.socket.disconnect()

elif user_type == 'producer':
    producer_id = sys.argv[3]
    cams = []
    for index in range(4, len(sys.argv)):
        cams.append(sys.argv[index])

    print('CONSTRUCTED PRODUCER CLIENT ENVIRONMENT')
    print('\tUSER-ID : ', user_id)
    print('\tPRODUCER-ID : ', producer_id)
    print('\tCAMERA-LIST : ', cams)
    client = Producer(user_id, producer_id, cams)
    count = 1
    message_count = 10000
    start = datetime.datetime.now()
    while count < message_count:
        time.sleep(1)
        time.sleep(sys.float_info.min)
        cams = client.camera_list
        for index in range(len(cams)):
            client.produce(cams[index], str(random.getrandbits(128)))
        if (count / message_count * 100) % 10 == 0:
            diff = datetime.datetime.now() - start
            print('PROGRESS ... ' + str(count / message_count * 100) + '% [' + str(diff.seconds) + 's]')
        count += 1
    diff = datetime.datetime.now() - start
    print('PRODUCER EXECUTED [' + str(client.send_count) + '] MESSAGES')
    print('PRODUCER EXECUTED FOR [' + str(diff.seconds) + '] SECONDS')

    if client.send_count / diff.seconds > 50:
        print('PRODUCER PASSED REQUIRED PERFORANCE TESTING WITH ' + str(client.send_count / diff.seconds) + '[messages/second]')
    else:
        print('PRODUCER FAILED REQUIRED PERFORANCE TESTING OF 50 [messages/second] - PLEASE TRY A MORE POWERFUL MACHINE!')

    assert(client.send_count / diff.seconds > 50)
    
    time.sleep(10)
    client.socket.disconnect()
