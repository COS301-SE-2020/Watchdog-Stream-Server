import time
from stream_user.user import Producer, Consumer

print('...TESTING REQUIRES SERVER RUNNING ON localhost...')

user_id = 'XXXUSERXXXIDXXX'
producer_id = 'XXXPRODUCERXXXIDXXX'


def test_add_clients():
    producer = Producer(user_id, producer_id)
    consumer = Consumer(user_id)

    assert producer is not None
    assert consumer is not None


def test_conflicting_clients():
    producer1 = Producer(user_id, producer_id)
    producer2 = Producer(user_id, producer_id)

    consumer1 = Consumer(user_id)
    consumer2 = Consumer(user_id)

    time.sleep(1)

    consumer1.set_cameras(producer_id, ['a1', 'b1', 'c1'])

    time.sleep(1)

    consumer2.set_cameras(producer_id, ['a2', 'b2', 'c2'])

    time.sleep(1)

    assert producer1.active is False
    assert producer2.active is True
