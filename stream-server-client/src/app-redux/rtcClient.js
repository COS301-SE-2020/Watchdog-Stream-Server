import socketIO from 'socket.io-client'
import { LIVE_SERVER_URL } from './constants'
import store from './store'
import moment from 'moment'


const socket = socketIO(LIVE_SERVER_URL, {
    secure: true,
})

function negotiate(pc, camera_id, socket) {
    console.log('Preparing Negotiation...')
    pc.addTransceiver('video', {direction: 'recvonly'});
    pc.addTransceiver('audio', {direction: 'recvonly'});
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        // return fetch('http://127.0.0.1:8081/offer', {
        //     body: JSON.stringify({
        //         sdp: offer.sdp,
        //         type: offer.type,
        //     }),
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        //     method: 'POST'
        // });
        console.log('Sending negotiate event...')
        socket.emit('negotiate', {
            camera_id,
            offer
        })
    }).catch(function(e) {
        alert(e);
    });
}

var SocketManager = (function () {

    var dispatch = null
    var user_id = null
    var config = {
        sdpSemantics: 'unified-plan',
        iceServers: [{urls: ['stun:stun.l.google.com:19302']}]

    };
    var pc = {};


    socket.on('connect', () => {

        dispatch({
            type: "LIVE_CONNECTED",
        })

        socket.on('disconnect', () => {
            dispatch({
                type: 'LIVE_DISCONNECTED'
            })
        })

        socket.on('registered', (data) => {
            console.log(data)
        })

        socket.on('camera-available', (data) => {
            console.log('camera-available: '+data.camera_id)
            dispatch({
                type: 'UPDATE_PRODUCERS',
                user_id,
                'data': data.camera_id
            })
        })

        socket.on('producer-answer', (data)=> {
            console.log('ANSWER: '+data)
            let camera_id = data['camera_id']
            let answer = data['answer']
            pc[camera_id].setRemoteDescription(answer).then((res) => {
                console.log('Setting remote description\t'+camera_id+"\t"+res)
            }).catch((err) => {
                console.log('Setting remote description FAILED!!L\t'+err)
            });
        })


    })

    return { // public interface
        init: function (dispatcher) {
            dispatch = dispatcher
        },
        connect: function () {
            console.log("CONNECTING TO LIVE SERVER");
            socket.connect()
        },
        disconnect: function () {
            socket.disconnect()
        },
        authorise: function () {
            user_id = store.getState().Data.user_id
            socket.emit('register', {
                user_id,
                client_type: 'consumer',
                data: {
                    test: 'hello'
                }
            })
        },
        tuneInToFeed: function (camera_list, site_id, producers) {
            console.log('Tuning in...')
            camera_list.forEach((camera_id) => {
                pc[camera_id] = new RTCPeerConnection(config);
                pc[camera_id]['camera_id'] = camera_id
                pc[camera_id].addEventListener('track', function(evt) {
                    if (evt.track.kind === 'video')
                        console.log(evt)
                        global[camera_id + "_stream"] = evt.streams[0];
                        document.getElementById(camera_id).srcObject = evt.streams[0];
                        document.getElementById(camera_id).controls = true;
                        document.getElementById(camera_id).style.width = '200';
                    // } else {
                    //     document.getElementById('audio').srcObject = evt.streams[0];
                    // }
                    dispatch({
                        type: 'CONSUME_VIEW',
                        camera_id: evt.currentTarget["camera_id"],
                        frame: 'on'
                    })
                });
                negotiate(pc[camera_id], camera_id, socket)
            })

        }
    };
})();

Object.freeze(SocketManager)
export default SocketManager
export const tuneIntoFeed = SocketManager.tuneInToFeed
export const authenticate = SocketManager.authorise