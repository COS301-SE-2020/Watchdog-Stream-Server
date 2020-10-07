# RTC Server

```shell script
python serve.py
```

##### Events:

- register: *registers a client as a consumer or producer*
```javascript
{
  "user_id": 'string',
  "client_type": "(consumer|producer)",
  "data": {} //Can leave it blank
}
```

- negotiate: *receives the offer from the consumer and sends it to the producer*
```javascript
{
    "camera_id": "string",
    "offer": {
        "type": "offer type",
        "sdp": "offer sdp"
    }
}
```
(emits 'offer')

- answer: *receives the answer from the producer (in response to the negotiate above) and sends it to the consumer that requested it*
```javascript
{
    "camera_id": "string",
    "answer": {} //the answer object from the producer
}
```
(emits 'producer-answer')

### Consumer

```shell script
cd stream-server-client
npm install
npm start
```

- **To Run**
    1. Cognito Login
    2. ControlPanel Fetch
    3. Authorise
    4. Tune-In

- **File Structure (files of importance)**
```
-- src
    |
    --- app-redux
    |       |
    |       --- rtcClient.js (Actual js consumer client)
    |
    --- App.js (UI elements that display the stream)
```

### Producer

```shell script
pip install -r requirements.txt
python -m stream_server_producer
```

- **File Structure (files of importance)**

```
-- rtc_producer.py (Actual python producer client)
|
-- __main__.py (to set the user_id and camera_id to mock)
```
