import axios from "axios";
import apiInstance from "./api";
import { refreshToken, endSession, isSessionExpired } from "./services/auth";
import setAlert from "../utils/setAlert";
import { COMPONENT_URL } from "../config/constant";
import i18next from "i18next";

const setup = (store) => {
  let isRefreshing = false;
  let refreshSubscribers = [];

  const subscribeTokenRefresh = (subscriber) => {
    refreshSubscribers.push(subscriber);
  };

  // The renewal is over before anyone is told: whoever subscribes from here on
  // is subscribing to the next one, not to a list that nobody is going to read
  const settleRenewal = (answer) => {
    const waiting = refreshSubscribers;
    refreshSubscribers = [];
    isRefreshing = false;
    waiting.forEach(answer);
  };

  const onRefreshed = (token) => {
    settleRenewal(({ resolve }) => resolve(token));
  };

  // Whatever was waiting for the new token has to be told that it is not
  // coming. Emptying the list without answering left every one of those
  // requests pending forever, and the screens waiting for them loading forever
  const onRefreshFailed = (error) => {
    settleRenewal(({ reject }) => reject(error));
  };

  // Answering a failure of the endpoints that hand out, renew or close the
  // session by renewing the session is what turned one expired token into a
  // cascade: the logout answers 401 when the token is already gone, which asked
  // for a renewal, which failed and logged out again. They all hang off the
  // same path, so naming the login covers the three
  const isSessionEndpoint = (url = "") =>
    [COMPONENT_URL.login, COMPONENT_URL.logout, COMPONENT_URL.refreshCookieToken].some((path) => url.includes(path));

  apiInstance.interceptors.request.use((request) => {
    const state = store.getState();
    const token = state.account.token;

    if (request.url.includes("refresh")) {
      delete apiInstance.defaults.headers.common["Authorization"];
    } else if (token) {
      request.headers.Authorization = `Bearer ${token}`;
      apiInstance.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }

    return request;
  });

  apiInstance.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      if (error.response === undefined) {
        setAlert(i18next.t("ngen.conection_failed"), "error");
        console.log("Network connection failed");
        return Promise.reject(error);
      }

      const originalRequest = error.config;

      if (error.response.data?.code === "token_not_valid" && !originalRequest._retry && !isSessionEndpoint(originalRequest.url)) {
        originalRequest._retry = true;

        // The token this request went out with may have been replaced while it
        // was travelling, by the renewal on activity or by another request that
        // got here first. Then there is nothing to renew: it was answered about
        // a token that is not the one of the session anymore, and asking for
        // another one so soon after the last is refused by the wait
        const current = store.getState().account.token;
        if (current && originalRequest.headers["Authorization"] !== `Bearer ${current}`) {
          originalRequest.headers["Authorization"] = `Bearer ${current}`;
          return axios(originalRequest);
        }

        if (!isRefreshing) {
          isRefreshing = true;
          refreshToken()
            .then((response) => {
              let newToken = response.data.access;
              onRefreshed(newToken);
            })
            .catch((refreshError) => {
              onRefreshFailed(refreshError);
              // The same rule the renewal on activity follows: only the api
              // saying that the refresh token is not valid anymore ends the
              // session. A 429, a backend that is restarting or a network that
              // dropped are moments that pass, and the session outlives them.
              // How long to wait before asking again, and whether the session
              // was already being closed, are kept by the service, so this path
              // and the renewal on activity wait and close together
              if (isSessionExpired(refreshError)) {
                endSession();
              }
            });
        }

        return new Promise((resolve, reject) => {
          subscribeTokenRefresh({
            resolve: (token) => {
              // replace the expired token and retry
              originalRequest.headers["Authorization"] = "Bearer " + token;
              return resolve(axios(originalRequest));
            },
            reject
          });
        });
      } else {
        if (originalRequest.avoidRaise) {
          return Promise.reject(error);
        }
        let data = error.response?.data;
        if (data === undefined) {
          console.error("API request failed: no response data", error.message);
        } else if (Array.isArray(data)) {
          console.error("API request failed:", data.join(" "));
        } else {
          let msg = error.response?.data?.non_field_errors
            || error.response?.data?.detail
            || error.response?.data?.__all__
            || "";
          console.error("API request failed:", msg || error.message);
        }
        return Promise.reject(error);
      }
    }
  );
};

export default setup;
