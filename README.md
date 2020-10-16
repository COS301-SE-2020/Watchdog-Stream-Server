# Watchdog - API

This repository contains all the code used in the API

### Watchdog Repositories
|[Home Control Panel](https://github.com/COS301-SE-2020/Watchdog)|[API](https://github.com/COS301-SE-2020/Watchdog-API)|[Front End](https://github.com/COS301-SE-2020/Watchdog-FrontEnd)|[Stream Server](hhttps://github.com/COS301-SE-2020/Watchdog-Stream-Server)|
|---|---|---|---|---|

### Project Description:

Home break-ins was rated the [number one crime]( http://www.statssa.gov.za/publications/P0341/P03412018.pdf) in South Africa in 2018/2019 period. There were about [1,3 million incidences of housebreaking affecting 5,8% of households in South Africa. Approximately 48% of affected households reported incidences to the police.](http://www.statssa.gov.za/?p=12614)

Watchdog set out to increase the number of reports to the police by providing the home owner with real-time notifications of tangible evidence of when possible intruders have been identified in their IP camera feed.

### Documentation

* [Software Requirements Specification](https://drive.google.com/file/d/1D6Jx3BDj6xvC9bDXCHUg7lry4IerSvTl/view)

- [Previous Software Requirements Specification Versions](https://drive.google.com/drive/folders/1g7gR9nS8uDv7q-Nas4mgqkys7NiExaZ3?usp=sharing)
- [Technical Installation Manual](https://drive.google.com/file/d/1RbIdqNwSCoAh9eayC3P642kQt1qZFQ-0/view?usp=sharing)
- [User Manual](https://drive.google.com/file/d/1FnLfaTkhfTK44cwfXVDfh9R2VatEGOh5/view?usp=sharing)
- [Coding Standards Document](https://drive.google.com/file/d/1X4IsmHWHwBjvmg1aaUua1HiC6rs6w5pO/view?usp=sharing)
- [Project Management Tool (Clubhouse)](https://app.clubhouse.io/lynksolutions/stories) (If you require access please email a team member and we will add you to our workspace, since clubhouse does not allow external viewing)


### Deployed Website Link:
- [Watchdog System](https://lynksolutions.watchdog.thematthew.me)

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

### The Team

|Member|Student #|Page|LinkedIn|
|------|---------|----|--------|
| Jonathan Sundy   | u18079581 | <https://jsundy.github.io>          | <https://www.linkedin.com/in/jonathen-sundy-79b33b168/>     |
| Ushir Raval      | u16013604 | <https://urishiraval.github.io>     | <https://www.linkedin.com/in/unraval/>                      |
|Jordan Manas|u17080534|<https://u17080534.github.io>|<https://www.linkedin.com/in/jordan-manas-b822651aa/>|
| Luqmaan Badat    | 17088519  | https://github.com/luqmaanbadat     | <https://www.linkedin.com/in/luqmaan-badat/>                |
| Aboobakr Kharbai | u18037306 | <https://abubakrk.github.io>        | <https://www.linkedin.com/in/aboobacker-kharbai-7a94961a9/> |
|Armin van Wyk|u18008632|<https://github.com/BigMacDaddy007>|<https://www.linkedin.com/in/armin-van-wyk-b714931a9/>|

<details>
<summary>
<h1>Profiles</h1>
</summary>
##### Jonathan Sundy

I have been exposed to an event-driven system that adopted modern cloud architecture that was hosted on Heroku and used a subset of AWS. I will use this knowledge gained to pioneer the system to be loosely coupled that promotes independent events triggering different parts of the system. Hence, I am certain that I will be of great value to the development of the serverless architecture. I am not too coherent with AWS but am motivated and inspired to expand my knowledge!

##### Ushir Raval

My exposure varies greatly from desktop applications to web based technologies, all in mostly a corporate “fintech” focused development environment. My skillset ranges from python development to web-based desktop applications using full stack technologies and my personal motto is “measure twice, cut once”. I prize scalable, robust and portable code above all else and intend to primarily contribute to the integration of various technologies such as the front-end to back-end communication etcetera.

##### Jordan Manas

An avid student of the numerous fields found within Computer Science, with a concentration in the field of Artificial Intelligence. Also being well-versed in Web Development, I recognize that I am capable of fulfilling important roles in the given project. I have experience in developing projects that use almost all of the proposed technologies and am very confident that our final product will be one of quality.

##### Luqmaan Badat

I am a final year computer science student. I am adaptable, reliable and keen to learn new programming technologies. My interests are software engineering, artificial intelligence and web development. My skills range include web development, full stack development, Java development and using full stack development technologies like docker and circleci. I’ve been exposed to and worked on cloud-based solutions in the medical field. 

##### Aboobakr Kharbai

My exposure ranges between desktop applications and web-based technologies. I am very reliable as well as trustworthy. I have a broad range of experience in backend development which includes database management systems, as well as experience in java development. I am one who is always steadfast in deadlines set out and will do anything in my capacity to ensure the work done is before the deadline and also of an industry standard.

##### Armin van Wyk

I have been involved in a multitude of projects inside and outside of the EBIT faculty. I have particular interest in front-end multimedia design to back-end REST API and hosting tasks. I have familiarity in databases both with and without SQ. I can use these skills in the request handling and data handling of our projects and ensure validated, clean and lightweight data.

</details>
