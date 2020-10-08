import React, { useEffect, useState, VideoHTMLAttributes } from 'react';
import logo from './logo.svg';
import static_image from './static.gif';
import { Container, Row, Col } from 'react-grid-system';
import { connect } from 'react-redux';
import SocketManager from './app-redux/rtcClient';
import './App.css';

import { tuneIntoFeed, authenticate } from './app-redux/rtcClient';
import { getControlPanel, getUserData } from './app-redux/actions';
import Amplify from 'aws-amplify';
import { Auth } from 'aws-amplify';

Amplify.configure({
  Auth: {

    // REQUIRED only for Federated Authentication - Amazon Cognito Identity Pool ID
    //identityPoolId: 'XX-XXXX-X:XXXXXXXX-XXXX-1234-abcd-1234567890ab',

    // REQUIRED - Amazon Cognito Region
    region: 'eu-west-1',

    // OPTIONAL - Amazon Cognito Federated Identity Pool Region 
    // Required only if it's different from Amazon Cognito Region
    identityPoolRegion: 'eu-west-1',

    // OPTIONAL - Amazon Cognito User Pool ID
    userPoolId: 'eu-west-1_mQ0D78123',

    // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
    userPoolWebClientId: 'lcrgnjetqoieui4dmg7m5h8t4',



  }
});






function App(props) {
  // useEffect(() => {
  //   SocketManager.connect()
  //   return function disconnect() {
  //     SocketManager.disconnect()
  //   }
  // })
  async function signIn(username, password) {
    try {
      const user = await Auth.signIn(username, password);
    } catch (error) {
      console.log('error signing in', error);
    }
    props.login()
  }

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);

  const renderCamera = (cameraObject, image, props) => {
    return <Col>
      <p>Name : {cameraObject.name}</p>
      <p>Location: {cameraObject.location}</p>
      <video
        style={{
          border: '3px solid',
          borderColor: (props.serverStatus) && (props.producers[cameraObject.id]) ? 'green' : 'red',
          margin: 5
        }}
        id={cameraObject.id}
        className={cameraObject.id}
        // ref={(video) => {
        //   if (global[cameraObject.id+"_stream"]) {
        //     console.log('Camera '+cameraObject.id+" updating...");
        //     console.log(global[cameraObject.id+"_stream"]);
        //     console.log(props.camera_frames)
        //   }
        //   if (video) {
        //     video.autoplay = true;
        //     video.controls = true;
        //     video.playsinline = true;
        //     video.srcObject = global[cameraObject.id+"_stream"];
        //   }
        // }}
      />
      <p>{props.camera_frames[cameraObject.id]}</p>
    </Col>
  }

  return (
    <div className="App">
      <header className="App-header">
        <Container>
          <Row>
            <div>
              <label>Username</label><br />
              <input name='username' type='text' value={username} onChange={(e) => setUsername(e.target.value)} />
              <br style={{ margin: 20 }} />
              <label>Password</label><br />
              <input name='password' type='password' value={password} onChange={(e) => setPassword(e.target.value)} /><br />
              <button onClick={() => { signIn(username, password).then((res) => setLoggedIn(true)) }}>Congnito Login</button>
            </div>
            <Col>
            </Col>
            <Col>
              <small>Connection to Server: <span style={{ color: (props.serverStatus == true) ? 'green' : 'red' }}>{props.serverStatus.toString()}</span></small>
              <hr />
              <small>Cognito Login: <span style={{ color: (loggedIn == true) ? 'green' : 'red' }}>{loggedIn.toString()}</span></small>
            </Col>
            <Col>
              <button onClick={() => props.fetch()}>Get ControlPanel (Dynamo)</button>
              <hr />
              <button onClick={() => props.authorize()}>Authenticate (On Stream Server)</button>
              <button onClick={() => props.tuneIn(props.cameras, [], props.producers)}>Tune In (Consume-View on Stream Server)</button>
              <button onClick={() => SocketManager.connect()}>Connect (Stream Server)</button>
              <button onClick={() => SocketManager.disconnect()}>Disconnect (Stream Server)</button>
            </Col>
          </Row>
        </Container>
      </header>
      <h3>Cameras</h3>
      <Container style={{ margin: 5 }}>
        <Row>

          <Col>
            <Row>

              {
                props.camera_objects.map((obj, i) => {
                  return renderCamera(obj, props.camera_frames[obj.id], props)
                })
              }
              <Col>
                <pre style={{ fontSize: 10 }}>
                  {JSON.stringify(props, undefined, 3)}
                </pre>
              </Col>
            </Row>
          </Col>
        </Row>
      </Container>
    </div>
  );
}


const mapStoreToProps = (store) => ({
  camera_objects: store.Data.camera_objects,
  cameras: store.Data.cameras,
  user_id: store.Data.user_id,
  camera_locations: store.Data.camera_locations,
  sites: store.Data.sites,
  loading: store.UI.ControlPanel.loading,
  serverStatus: store.Live.status,
  producers: store.Live.producers,
  camera_frames: store.Live.frames
})

const mapDispatchToProps = (dispatch, ownProps) => ({
  login: () => {
    dispatch(getUserData())
    dispatch(getControlPanel())
  },
  fetch: () => {
    dispatch(getControlPanel())
  },
  tuneIn: (camera_list, site_id, producers) => tuneIntoFeed(camera_list, site_id, producers),
  authorize: () => authenticate()
})

export default connect(
  mapStoreToProps, mapDispatchToProps
)(App);
