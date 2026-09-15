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
// The answer of a renewal that is already travelling is the answer both callers
// are waiting for, so the second one joins it instead of asking again
let renewalInFlight = null;
// Closing a session takes a request, and until it answers the token is still in
// the store: without this the activity of the user keeps starting renewals and
// logouts against a session that is already over, and says so once per try
let closing = false;
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
 * Two places ask for the same thing, the renewal on activity and the retry of a
 * request that was answered that its token is not valid, and they can ask at
 * the same moment: coming back to a tab wakes the first one and the requests of
 * the page at once. Whoever arrives second waits for the answer that is already
 * on its way.
 *
 * With nothing travelling it refuses while it is waiting, so neither caller can
 * turn a failure into a stream of requests against an endpoint that is already
 * saying no. Neither the refusal nor the wait is the session ending, so nobody
 * logs out over them
 */
const refreshToken = () => {
  if (closing) {
    // The session is on its way out and the token is only still in the store
    // because closing it takes a request: renewing it would be asking for a
    // token to throw away, once every wait for as long as the logout takes
    return Promise.reject(closedSessionError());
  }
  // A store with no session has nothing to renew. The refresh cookie outlives
  // the logout, so an answer landing here afterwards would hand back a token
  // and stand a session up that nobody is in, with no user behind it
  if (!store.getState().account?.token) {
    return Promise.reject(closedSessionError());
  }
  if (renewalInFlight) {
    return renewalInFlight;
  }
  if (Date.now() < renewalNotBefore) {
    return Promise.reject(postponedError());
  }
  renewalNotBefore = Date.now() + MIN_INTERVAL_MS;
  const generation = sessionGeneration;

  renewalInFlight = apiInstance
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
    })
    .finally(() => {
      renewalInFlight = null;
    });

  return renewalInFlight;
};

/**
 * The one way a session ends because it is over. Both the renewal on activity
 * and the retry of a request can find out at the same time, and the answer is
 * the same: say it once and close it once
 */
const endSession = () => {
  if (closing) {
    return;
  }
  setAlert(i18next.t("ngen.auth.session_expired"), "error");
  logout(true);
};

const _doLogout = (save_url) => {
  const { dispatch } = store;
  renewalNotBefore = 0;
  renewalBackoff = BACKOFF_FIRST_MS;
  closing = false;
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
  // From here on the session is over, whoever asked: what is left in the store
  // until the api answers is not something to renew or to announce again, and
  // a renewal that was already travelling belongs to the session that is being
  // closed. Counting it from the answer of the api instead of from here left
  // the token that came back in the store, logged in, and the requests that
  // were waiting for it on their way out
  closing = true;
  sessionGeneration += 1;
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

export { register, login, refreshToken, logout, endSession, sessionPayload, isSessionExpired };
