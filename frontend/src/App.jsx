import React from "react";
import { BrowserRouter } from "react-router-dom";
import { useIdleTimer } from "react-idle-timer";
import store from "./store";

import routes, { renderRoutes } from "./routes";
import { logout, refreshToken } from "./api/services/auth";

const App = () => {
  const onIdle = () => {
    if (store.getState().account.token) {
      logout(true);
    }
  };

  const onAction = () => {
    const state = store.getState();
    const token = state.account.token;
    const iat = state.account.iat;
    const exp = state.account.exp;
    if (!token || !iat || !exp) {
      return;
    }
    // check if token iat has more than X seconds, if so refresh token
    const currentTime = Date.now() / 1000;
    const secondsWindow = 60; // TODO: Change to backend configuration
    if (iat + secondsWindow < currentTime) {
      refreshToken().catch(() => {
        logout(true);
      });
    } else {
      if (exp < currentTime) {
        logout(true);
      }
    }
  };

  useIdleTimer({
    onIdle,
    onAction,
    timeout: 1000 * 60 * 14, // TODO: Change to backend configuration and equal this to refresh token expiration time - 1 minute
    promptBeforeIdle: 0,
    events: [
      "mousemove",
      "keydown",
      "wheel",
      "DOMMouseScroll",
      "mousewheel",
      "mousedown",
      "touchstart",
      "touchmove",
      "MSPointerDown",
      "MSPointerMove",
      "visibilitychange",
      "focus"
    ],
    immediateEvents: [],
    debounce: 0,
    throttle: 0,
    eventsThrottle: 1000,
    element: document,
    startOnMount: true,
    startManually: false,
    stopOnIdle: false,
    crossTab: true,
    name: "idle-timer",
    syncTimers: 1000,
    leaderElection: false
  });

  return <BrowserRouter basename={import.meta.env.VITE_APP_BASE_NAME}>{renderRoutes(routes)}</BrowserRouter>;
};

export default App;
