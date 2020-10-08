import asyncio
import sys
import time
import datetime
import random
from .rtc_producer import RTCConnectionHandler
import platform

# producer user_id prod_id cam_id1 cam_id2 cam_id3 cam_id4 ...
# consumer user_id - prod_id1 cam_id1 cam_id2 - prod_id2 cam_id3 cam_id4 ...

# user_type = sys.argv[1]
# user_id = sys.argv[2]

time.sleep(random.randint(1, 10))

print('STARTING STREAM SERVER CLIENT TESTING ENVIRONMENT')
user_id = 'b0db8f1c-745d-4d46-9b4c-c30f2ef05637'
cams = ['c16e99484593b74706fedba2b2786b36abf28b171848ceb5a2db44666e71ffc7c',
        'cc465f21cb97b3c1cd14569cdaf7fa50fe02107b05bd5411c32f583944bf5d86a']

print('CONSTRUCTED PRODUCER CLIENT ENVIRONMENT')
print('\tUSER-ID : ', user_id)
# print('\tPRODUCER-ID : ', producer_id)
print('\tCAMERA-LIST : ', cams)


async def start():
    clients = {}
    for camera_id in cams:
        clients[camera_id] = RTCConnectionHandler(user_id=user_id, camera_id=camera_id)
        await clients[camera_id].start()
        await clients[camera_id].register()
        await clients[camera_id].make_view_available()
    await asyncio.sleep(1000)


if platform.system() == 'Darwin':
    asyncio.get_event_loop().run_until_complete(start())
else:
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())

# time.sleep(10)
# client.socket.disconnect()
