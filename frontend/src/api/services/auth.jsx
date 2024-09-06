import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";
import { LOGIN, LOGOUT, REFRESH_TOKEN, SAVE_URL } from "../../store/actions";
import store from "../../store";
import i18next from "i18next";
import { jwtDecode } from "jwt-decode";

const register = (username, password, email) => {
  return apiInstance
    .post(COMPONENT_URL.register, {
      username: username,
      password: password,
      email: email,
      is_active: true
    })
    .then((response) => {
      setAlert(i18next.t("ngen.auth.register.success"), "success");
      return response;
    })
    .catch((error) => {
      setAlert(i18next.t("ngen.auth.register.error"), "error");
      return Promise.reject(error);
    });
};

const login = (username, password) => {
  apiInstance
    .post(COMPONENT_URL.login, {
      username: username,
      password: password
    })
    .then((response) => {
      let decoded = jwtDecode(response.data.access);
      const { dispatch } = store;
      dispatch({
        type: LOGIN,
        payload: {
          user: response.data.user,
          token: response.data.access,
          iat: decoded.iat,
          exp: decoded.exp,
          user_id: decoded.user_id
        }
      });
      return response;
    })
    .catch((error) => {
      console.log(error);
      if (error.response.data.detail === "La combinación de credenciales no tiene una cuenta activa") {
        setAlert(i18next.t("ngen.auth.login.invalidCredentials"), "error");
      } else {
        setAlert(i18next.t("ngen.auth.login.error"), "error");
      }
      return Promise.reject(error);
    });
};

const refreshToken = () => {
  return apiInstance
    .post(COMPONENT_URL.refreshCookieToken, {})
    .then((response) => {
      let decoded = jwtDecode(response.data.access);
      const { dispatch } = store;
      try {
        dispatch({
          type: REFRESH_TOKEN,
          payload: {
            token: response.data.access,
            iat: decoded.iat,
            exp: decoded.exp
          }
        });

        return response;
      } catch (e) {
        console.log(e);
        console.log("Error en el dispatch refreshToken");
      }
    })
    .catch((error) => {
      console.log(error);
      logout(true);
      return Promise.reject(error);
    });
};

const logout = (save_url = false) => {
  return apiInstance
    .post(COMPONENT_URL.logout)
    .then(() => {
      const { dispatch } = store;
      try {
        // localStorage.clear();
        localStorage.removeItem("ngen-account");
        localStorage.removeItem("ngen-message");
        if (save_url) {
          dispatch({
            type: SAVE_URL,
            payload: {
              url: save_url === true ? window.location.pathname : null
            }
          });
        }
        dispatch({
          type: LOGOUT
        });
        document.title = "NGEN";
      } catch (e) {
        console.log(e);
        console.log("Error en el dispatch logout");
      }
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

export { register, login, refreshToken, logout };
