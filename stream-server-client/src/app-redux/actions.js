import * as actionTypes from './actionTypes';
import { Auth } from 'aws-amplify'

export function getUserData() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.GET_USER_DATA, actionTypes.GET_USER_DATA_SUCCESS, actionTypes.GET_USER_DATA_FAIL],
                        payload: {
                            request: {
                                url: '/user',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function getSecurityLevel() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                // console.log(jwt)
                dispatch(
                    {
                        types: [actionTypes.GET_SECURITYLEVEL, actionTypes.GET_SECURITYLEVEL_SUCCESS, actionTypes.GET_SECURITYLEVEL_FAIL],
                        payload: {
                            request: {
                                url: '/preferences/securitylevel',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function updateSecurityLevel(security_level) {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.UPDATE_SECURITYLEVEL, actionTypes.UPDATE_SECURITYLEVEL_SUCCESS, actionTypes.UPDATE_SECURITYLEVEL_FAIL],
                        payload: {
                            request: {
                                method: 'post',
                                url: '/preferences/securitylevel',
                                headers: {
                                    Authorization: `${jwt}`
                                },
                                data: {
                                    security_level
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function getRecordings() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.GET_RECORDINGS, actionTypes.GET_RECORDINGS_SUCCESS, actionTypes.GET_RECORDINGS_FAIL],
                        payload: {
                            request: {
                                url: '/ui/recordings',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function getIdentities() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.GET_IDENTITIES, actionTypes.GET_IDENTITIES_SUCCESS, actionTypes.GET_IDENTITIES_FAIL],
                        payload: {
                            request: {
                                url: '/detectintruder',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function uploadIdentity(name, filename, file) {
    return (dispatch, getState) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                Promise.all([
                    dispatch(
                        {
                            types: [actionTypes.GET_IDENTITIES_UPLOAD, actionTypes.GET_IDENTITIES_UPLOAD_SUCCESS, actionTypes.GET_IDENTITIES_UPLOAD_FAIL],
                            payload: {
                                request: {
                                    method: 'post',
                                    url: '/identities/upload',
                                    headers: {
                                        Authorization: `${jwt}`
                                    },
                                    params: {
                                        name,
                                        filename,
                                        tag: 'whitelist'
                                    }
                                }
                            }
                        }
                    )
                ]).then(res => {
                    // console.log(getState().UI.Identities.uploadData);
                    const whitelist_upload_queue = { ...getState().UI.Identities.uploadData }
                    console.log({ "WHITELSIT": whitelist_upload_queue });
                    const fields = whitelist_upload_queue.fields
                    const url = whitelist_upload_queue.url

                    const formData = new FormData()
                    for (let key in fields) {
                        formData.append(key, fields[key])
                    }
                    const type = 'image'
                    formData.append('file', { uri: file, name: filename, type })

                    dispatch(
                        {
                            types: [actionTypes.UPLOAD_TO_S3, actionTypes.UPLOAD_TO_S3_SUCCESS, actionTypes.UPLOAD_TO_S3_FAIL],
                            payload: {
                                request: {
                                    client: 'generic',
                                    method: 'post',
                                    url: url,
                                    data: formData
                                }
                            }
                        }
                    )
                }).catch((error) => {
                    dispatch(
                        {
                            type: actionTypes.UPLOAD_TO_S3_FAIL,
                            error
                        }
                    )
                })
            }
        )
    }
}

export function getLogs() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.GET_LOGS, actionTypes.GET_LOGS_SUCCESS, actionTypes.GET_LOGS_FAIL],
                        payload: {
                            request: {
                                url: '/logs',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function getControlPanel() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.GET_CONTROLPANEL, actionTypes.GET_CONTROLPANEL_SUCCESS, actionTypes.GET_CONTROLPANEL_FAIL],
                        payload: {
                            request: {
                                url: '/controlpanel',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function getPreferences() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.GET_PREFERENCES, actionTypes.GET_PREFERENCES_SUCCESS, actionTypes.GET_PREFERENCES_FAIL],
                        payload: {
                            request: {
                                url: '/preferences',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function getDetected() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.GET_DETECTED, actionTypes.GET_DETECTED_SUCCESS, actionTypes.GET_DETECTED_FAIL],
                        payload: {
                            request: {
                                url: '/identities/tagdetectedimage',
                                headers: {
                                    Authorization: `${jwt}`
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function updateDetectedImage(key, name) {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.UPDATE_DETECTEDIMAGE, actionTypes.UPDATE_DETECTEDIMAGE_SUCCESS, actionTypes.UPDATE_DETECTEDIMAGE_FAIL],
                        payload: {
                            request: {
                                method: 'post',
                                url: '/identities/tagdetectedimage',
                                headers: {
                                    Authorization: `${jwt}`
                                },
                                params: {
                                    key,
                                    name
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function updateNotificationPreferences(security_company, type) {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        types: [actionTypes.UPDATE_NOTIFICATION_PREFERENCES, actionTypes.UPDATE_NOTIFICATION_PREFERENCES_SUCCESS, actionTypes.UPDATE_NOTIFICATION_PREFERENCES_FAIL],
                        payload: {
                            request: {
                                method: 'post',
                                url: '/preferences/notifications',
                                headers: {
                                    Authorization: `${jwt}`
                                },
                                params: {
                                    security_company,
                                    type
                                }
                            }
                        }
                    }
                )
            }
        )
    }
}

export function connectToFeed(camera_list, site_id) {
    return (dispatch) => {
        dispatch({
            type: "START_STREAM",
            view: {
                site_id, camera_list
            }
        })
    }
}

export function authorizeServerConnection() {
    return (dispatch) => {
        Auth.currentSession().then(
            idToken => {
                let jwt = idToken.getIdToken().getJwtToken()
                dispatch(
                    {
                        type: 'AUTHENTICATE_STREAM'
                    }
                )
            }
        )
    }
}