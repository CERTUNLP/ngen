import apiInstance from "../api";
import { COMPONENT_URL } from '../../config/constant';
import setAlert from '../../utils/setAlert';
import { REFRESH_TOKEN, LOGOUT, CLEAR_MESSAGE } from '../../store/actions';
import { store } from '../../store';
import i18next from "i18next";

const register = (username, password, email) => {
    return apiInstance.post(COMPONENT_URL.register, {
        username: username,
        password: password,
        email: email,
        is_active: true
    }).then(response => {
        setAlert(i18next.t('ngen.auth.register.success'), "success");
        return response;
    }).catch(error => {
        setAlert(i18next.t('ngen.auth.register.error'), "error");
        return Promise.reject(error);
    });
}

const login = (username, password) => {
    return apiInstance.post(COMPONENT_URL.login, {
        username: username,
        password: password,
    }).catch(error => {
        if (error.response.data.detail === "La combinación de credenciales no tiene una cuenta activa") {
            setAlert(i18next.t('ngen.auth.login.invalidCredentials'), "error");
        } else {
            setAlert(i18next.t('ngen.auth.login.error'), "error");
        }
        return Promise.reject(error);
    });
}

const refreshToken = () => {
    return apiInstance.post(COMPONENT_URL.refreshCookieToken, {})
        .then(response => {
            const { dispatch } = store;
            try {
                dispatch({
                    type: REFRESH_TOKEN,
                    payload: { token: response.data.access }
                });

                return response;
            } catch (e) {
                console.log('Error en el dispatch')
            }
        })
        .catch(error => {
            const { dispatch } = store;
            try {
                dispatch({
                    type: LOGOUT
                });
                dispatch({
                    type: CLEAR_MESSAGE
                });
            } catch (e) {
                console.log('Error en el dispatch')
            }

            return Promise.reject(error);
        });
}

const logout = () => {
    return apiInstance.post(COMPONENT_URL.logout)
        .catch(error => {
            return Promise.reject(error);
        });
}

export { register, login, refreshToken, logout };
