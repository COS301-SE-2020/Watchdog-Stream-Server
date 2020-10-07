import { combineReducers } from 'redux';
import { produce } from 'immer';
import moment from 'moment'
import * as actions from './actionTypes';

var defaultState = require('./defaultState.json');

/**
 * Data Reducer to perform Data updates only
 * @param {*} state UserData update to give/update data in store
 * @param {*} action Redux Action
 */
function dataReducer(state = defaultState.UserData, action) {
    switch (action.type) {
        case actions.GET_USER_DATA_SUCCESS:
            return produce(state, draft => {
                draft.control_panel = action.payload.data.data.control_panel
                draft.logs = action.payload.data.data.logs
                draft.name = action.payload.data.data.name
                draft.preferences = action.payload.data.data.preferences
                draft.security_level = action.payload.data.data.security_level
                // draft.identities = action.payload.data.data.identities
                draft.user_id = action.payload.data.data.user_id
            })
        case actions.GET_RECORDINGS_SUCCESS:
            return produce(state, draftState => {
                draftState.videos = action.payload.data.data.videos
                draftState.locations = action.payload.data.data.locations
            })
        case actions.GET_IDENTITIES_SUCCESS:
            return produce(state, draft => {
                // console.log(action);
                draft.identities.profiles = action.payload.data.data.profiles
            })
        case actions.GET_LOGS_SUCCESS:
            // console.log("HERE");
            // console.log(action);
            return produce(state, draft => {
                draft.logs = action.payload.data.data.logs
            })
        case actions.GET_SECURITYLEVEL_SUCCESS:
            return produce(state, draft => {
                draft.preferences.security_level = action.payload.data.data.preferences.security_level
            })

        //Uploads and Updates
        case actions.UPDATE_SECURITYLEVEL_SUCCESS:
            return produce(state, draft => {
                draft.preferences.security_level = action.payload.data.data.Attributes.preferences.security_level
            })
        case actions.GET_IDENTITIES_UPLOAD_SUCCESS:
            return produce(state, draft => {
                draft.identities.whitelist_upload_queue = action.payload.data.data
            })
        case actions.GET_CONTROLPANEL_SUCCESS:
            let control_panel = action.payload.data.data.control_panel
            let cameras = []
            let locations = []
            let sites = Array.from(Object.keys(control_panel))
            let camera_objects = []

            sites.forEach((site) => {
                let loc = Array.from(Object.keys(control_panel[site]))
                locations = [...locations, ...loc]
                loc.forEach((location) => {
                    let cams = Array.from(Object.keys(control_panel[site][location]))
                    cameras = [...cameras, ...cams]
                    cams.forEach((camera) => {
                        control_panel[site][location][camera]['site'] = site
                        control_panel[site][location][camera]['location'] = location
                        control_panel[site][location][camera]['id'] = camera
                        camera_objects.push(control_panel[site][location][camera])
                    })
                })

            })

            return produce(state, draft => {
                draft.control_panel = action.payload.data.data.control_panel
                draft.camera_objects = camera_objects
                draft.cameras = cameras
                draft.camera_locations = locations
                draft.sites = sites
            })
        case actions.GET_PREFERENCES_SUCCESS:
            return produce(state, draft => {
                console.log(action.payload.data);
                draft.preferences = action.payload.data.data.preferences
            })
        case actions.UPDATE_NOTIFICATION_PREFERENCES_SUCCESS:
            return produce(state, draft => {
                // draft.preferences.notifications = action.payload.data.data.preferences.notifications
                // console.log(action.payload.data);
            })
        case actions.GET_DETECTED_SUCCESS:
            return produce(state, draft => {
                draft.identities.detected = action.payload.data.data.frames
            })
        case "EDIT_NOTIFICATIONS":
            return produce(state, draft => {
                draft.preferences.notifications.security_company = action.data.security_company
                draft.preferences.notifications.type = action.data.type
            })

        default:
            return state
    }
}

/**
 * UI Reducer to Map progress of API and other such related business logic
 * @param {*} state UI component states to indicate progression of API calls
 * @param {*} action Redux Action
 */
function uiReducer(state = defaultState.UI, action) {
    switch (action.type) {
        /**
         * Loading Notifiers
         */
        case actions.GET_USER_DATA:
            return produce(state, draft => {
                draft.Identities.loading = true
                draft.Logs.loading = true
            })
        case actions.GET_IDENTITIES:
            return produce(state, draft => {
                draft.Identities.loading = true
            })
        case actions.GET_RECORDINGS:
            return produce(state, draftState => {
                draftState.Recordings.loading = true
            })
        case actions.GET_LOGS:
            return produce(state, draftState => {
                draftState.Logs.loading = true
            })
        case actions.GET_SECURITYLEVEL:
            return produce(state, draft => {
                draft.SecurityLevel.loading = true
            })
        case actions.UPDATE_SECURITYLEVEL:
            return produce(state, draft => {
                draft.SecurityLevel.updating = true
            })
        case actions.GET_IDENTITIES_UPLOAD:
            return produce(state, draft => {
                draft.Identities.updating = true
            })
        case actions.UPLOAD_TO_S3:
            return produce(state, draft => {
                draft.Identities.uploading = true
            })
        case actions.GET_PREFERENCES:
            return produce(state, draft => {
                draft.Preferences.loading = true
            })
        case actions.UPDATE_NOTIFICATION_PREFERENCES:
            return produce(state, draft => {
                draft.Notifications.uploading = true
            })
        case actions.GET_CONTROLPANEL:
            return produce(state, draft => {
                draft.ControlPanel.loading = true
            })
        case actions.GET_DETECTED:
            return produce(state, draft => {
                draft.Detected.loading = true
            })

        /**
         * Success Notifiers
         */
        case actions.GET_USER_DATA_SUCCESS:
            return produce(state, (draftState) => {
                draftState.Identities.loading = false
                draftState.Logs.loading = false
            })
        case actions.GET_RECORDINGS_SUCCESS:
            return produce(state, (draftState) => {
                draftState.Recordings.loading = false
                draftState.Recordings.filteredVideos = action.payload.data.data.videos
            })
        case actions.GET_IDENTITIES_SUCCESS:
            return produce(state, (draftState) => {
                draftState.Identities.loading = false
            })
        case actions.GET_LOGS_SUCCESS:
            return produce(state, (draftState) => {
                draftState.Logs.loading = false
            })
        case actions.GET_SECURITYLEVEL_SUCCESS:
            return produce(state, draft => {
                draft.SecurityLevel.loading = false
            })
        case actions.UPDATE_SECURITYLEVEL_SUCCESS:
            return produce(state, draft => {
                draft.SecurityLevel.updating = false
            })
        case actions.GET_IDENTITIES_UPLOAD_SUCCESS:
            return produce(state, draft => {
                draft.Identities.uploadData = action.payload.data.data
            })
        case actions.UPLOAD_TO_S3_SUCCESS:
            return produce(state, draft => {
                draft.Identities.uploading = false
            })
        case actions.GET_PREFERENCES_SUCCESS:
            return produce(state, draft => {
                draft.Preferences.loading = false
            })
        case actions.UPDATE_NOTIFICATION_PREFERENCES_SUCCESS:
            return produce(state, draft => {
                draft.Notifications.uploading = false
            })
        case actions.GET_CONTROLPANEL_SUCCESS:
            return produce(state, draft => {
                draft.ControlPanel.loading = false
            })
        case actions.GET_DETECTED_SUCCESS:
            return produce(state, draft => {
                draft.Detected.loading = false
            })

        /**
         * Fail notifiers
         */
        //FIXME: Implement better error handling
        case actions.GET_USER_DATA_FAIL:
            return state
        case actions.GET_RECORDINGS_FAIL:
            return state
        case actions.GET_IDENTITIES_FAIL:
            return state
        case actions.GET_LOGS_FAIL:
            console.log("ERROR HERE");
            return state
        case actions.GET_SECURITYLEVEL_FAIL:
            return state
        case actions.UPDATE_SECURITYLEVEL_FAIL:
            return state
        case actions.UPLOAD_TO_S3_FAIL:
            return produce(state, draft => {
                draft.Identities.uploading = false
            })
        case actions.GET_CONTROLPANEL_FAIL:
            return produce(state, draft => {
                draft.ControlPanel.loading = false
            })
        case actions.GET_DETECTED_FAIL:
            return produce(state, draft => {
                draft.Detected.loading = true
            })

        default:
            return state;
    }
}

function statisticsReducer(state = {}, action) {
    switch (action.type) {
        default:
            return state
    }
}



function liveReducer(state = defaultState.Live, action) {
    switch (action.type) {
        case "LIVE_CONNECTED":
            return produce(state, draft => {
                draft.status = true
            })
        case "UPDATE_PRODUCERS":
            // console.log("UPDATE PRODUCERS -----------------")
            return produce(state, draft => {
                draft.producers.push(action.data.camera_id)
            })
        case "LIVE_DISCONNECTED":
            return produce(state, draft => {
                draft.status = false
            })
        case "START_STREAM":
            return produce(state, draft => {
                // action.view.camera_list.forEach((id) => {
                //     draft.frames[id] = 'inactive_black.png'
                // })

                draft.consume.site_id = action.view.site_id
                draft.consume.camera_list = action.view.camera_list
            })
        case "CONSUME_FRAME":
            return produce(state, draft => {
                draft.frames[action.camera_id] = action.frame
            })
        default:
            return state
    }
}

const watchdogApp = combineReducers(
    {
        "Data": dataReducer,
        "UI": uiReducer,
        "Statistics": statisticsReducer,
        "Live": liveReducer
    }
);

export default watchdogApp;