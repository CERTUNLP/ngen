import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";
import { LOGIN, LOGOUT, REFRESH_TOKEN, SAVE_URL } from "../../store/actions";
import store from "../../store";
import i18next from "i18next";
import { jwtDecode } from "jwt-decode";

/**
 * What the server signs (iat, exp) is written with the clock of the server, so
 * it says nothing to a browser whose clock is off: only the difference between
 * the two, the lifetime, travels between machines. The moment the token was
 * received is measured here, with the same clock that will later ask how old it
 * is, and every place that stores a session goes through this so none of them
 * can forget it.
 */
const sessionPayload = (accessToken) => {
  const decoded = jwtDecode(accessToken);
  return {
    token: accessToken,
    iat: decoded.iat,
    exp: decoded.exp,
    user_id: decoded.user_id,
    lifetime: decoded.exp - decoded.iat,
    obtainedAt: Date.now()
  };
};

/**
 * The only answer that means the session is really over: the api says so when
 * the refresh cookie is missing, expired or not valid anymore. Being refused
 * for asking too often, a backend that is restarting or a network that dropped
 * are moments that pass, and throwing the user out on those loses the work on
 * the screen for nothing.
 */
const isSessionExpired = (error) => error?.response?.data?.code === "token_not_valid";

/**
 * How long the api asked to wait, when it did
 */
const retryAfterMs = (error, fallback) => {
  const seconds = Number(error?.response?.headers?.["retry-after"]);
  return Number.isFinite(seconds) && seconds > 0 ? seconds * 1000 : fallback;
};

// Renewing is the one request the frontend makes on its own, and two places ask
// for it: the renewal on activity and the retry of a request that was answered
// that its token is not valid. How often it can be asked for is decided here,
// once, or one of the two keeps asking while the other is waiting
const MIN_INTERVAL_MS = 15 * 1000;
const BACKOFF_FIRST_MS = 5 * 1000;
const BACKOFF_MAX_MS = 2 * 60 * 1000;

let renewalNotBefore = 0;
let renewalBackoff = BACKOFF_FIRST_MS;
// A session that was closed can not be brought back by an answer that was
// already on its way: what comes back is only kept if it belongs to the session
// that asked for it
let sessionGeneration = 0;

const postponedError = () => {
  const error = new Error("Token renewal postponed");
  error.renewalPostponed = true;
  return error;
};

const closedSessionError = () => {
  const error = new Error("The session was closed while the token was renewed");
  error.sessionClosed = true;
  return error;
};

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
      const { dispatch } = store;
      dispatch({
        type: LOGIN,
        payload: {
          user: response.data.user,
          ...sessionPayload(response.data.access)
        }
      });
      return response;
    })
    .catch((error) => {
      // console.log(error);
      if (error.response?.data?.detail && error.status === 401) {
        setAlert(i18next.t("ngen.auth.login.invalidCredentials"), "error");
      } else if (error.message) {
        setAlert(`${i18next.t("ngen.auth.login.error")}: ${error.message}`, "error");
      } else {
        setAlert(i18next.t("ngen.auth.login.error"), "error");
      }
      return Promise.reject(error);
    });
};

/**
 * Asks for a new token and nothing else: whether a failure is worth closing the
 * session is for whoever called to decide, and it used to be decided twice
 * -here and in the caller- which logged the user out two times over.
 *
 * It refuses while it is waiting, so neither of the two callers can turn a
 * failure into a stream of requests against an endpoint that is already saying
 * no. The refusal is not the session ending, so nobody logs out over it
 */
const refreshToken = () => {
  if (Date.now() < renewalNotBefore) {
    return Promise.reject(postponedError());
  }
  renewalNotBefore = Date.now() + MIN_INTERVAL_MS;
  const generation = sessionGeneration;

  return apiInstance
    .post(COMPONENT_URL.refreshCookieToken, {})
    .then((response) => {
      if (generation !== sessionGeneration) {
        // The user logged out while this was travelling, and storing it would
        // put the session back on its feet with a token nobody asked for
        return Promise.reject(closedSessionError());
      }
      const { dispatch } = store;
      dispatch({
        type: REFRESH_TOKEN,
        payload: sessionPayload(response.data.access)
      });
      renewalBackoff = BACKOFF_FIRST_MS;
      return response;
    })
    .catch((error) => {
      if (!isSessionExpired(error) && !error.sessionClosed) {
        // What the api asks for, but never under the floor: it answers with
        // what is left of the window over the requests that fit in it, which
        // is one second often enough to become a flood of its own
        renewalNotBefore = Date.now() + Math.max(MIN_INTERVAL_MS, retryAfterMs(error, renewalBackoff));
        renewalBackoff = Math.min(renewalBackoff * 2, BACKOFF_MAX_MS);
      }
      return Promise.reject(error);
    });
};

const _doLogout = (save_url) => {
  const { dispatch } = store;
  // Whatever renewal is on its way belongs to the session that is ending here
  sessionGeneration += 1;
  renewalNotBefore = 0;
  renewalBackoff = BACKOFF_FIRST_MS;
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
}

const logout = (save_url = false) => {
  return apiInstance
    .post(COMPONENT_URL.logout)
    .catch(() => {
      // Best effort: this asks for a token that may be gone already, and the
      // session is being closed either way. Rejecting from here only left
      // unhandled rejections behind, since nobody waits for this
    })
    .finally(() => {
      try {
        _doLogout(save_url);
      } catch (e) {
        console.log("Error en el dispatch logout: " + e);
      }
    });
};

export { register, login, refreshToken, logout, sessionPayload, isSessionExpired };
