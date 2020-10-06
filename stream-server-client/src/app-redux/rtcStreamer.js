import socketIO from 'socket.io-client'
import { LIVE_SERVER_URL } from './constants'
import store from './store'


const socket = socketIO(LIVE_SERVER_URL, {
    secure: true,
})

function negotiate(pc, socket, camera_id) {
    pc.addTransceiver('video', { direction: 'recvonly' });

    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        // wait for ICE gathering to complete
        return new Promise(function (resolve) {
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
    })
}

var SocketManager = (function () {

    var dispatch = null
    var user_id = null
    var pc = {}
    var config = {
        sdpSemantics: 'unified-plan',
        iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }]
    }

    socket.on('connect', () => {

        dispatch({
            type: "LIVE_CONNECTED",
        })

        socket.on('disconnect', () => {
            dispatch({
                type: 'LIVE_DISCONNECTED'
            })
        })

        socket.on('available-views',
            (data) => {
                // socket.emit('consume-view', data)
                dispatch({
                    type: "UPDATE_PRODUCERS",
                    data,
                    user_id
                })
            }
        )

        //TODO: add event name
        socket.on('connected-rtc', (data) => {
            let answer = {
                type: data.type,
                sdp: data.sdp
            }
            pc[data.camera_id].setRemoteDescription(answer);
        });

        socket.on("consume-frame", (message) => {
            dispatch({
                type: "CONSUME_FRAME",
                camera_id: message.camera_id,
                frame: message.streams[0]
            })
        })

        setInterval(() => {
            socket.emit('pulse', { 'available_cameras': true })
        }, 5)
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
            console.log("AUTHENTICATING " + user_id);
            socket.emit('authorize', {
                user_id: user_id,
                client_type: 'consumer',
                client_key: 'string'
            })
        },
        tuneInToFeed: function (camera_list, site_id, producers) {
            let promises = camera_list.map(camera_id => {
                if (!pc[camera_id])
                    pc[camera_id] = new RTCPeerConnection(config);
                return negotiate(pc[camera_id], socket, camera_id);
            });

            Promise.all(promises).then(values => {
                let connections = {}
                values.forEach((camera_id, i) => {
                    connections[camera_id] = {
                        sdp: values[i].sdp,
                        type: values[i].type
                    }
                });
                socket.emit('consume-rtc', {
                    connections
                })
            })
        }
    };
})();

Object.freeze(SocketManager)
export default SocketManager
export const tuneIntoFeed = SocketManager.tuneInToFeed
export const authenticate = SocketManager.authorise