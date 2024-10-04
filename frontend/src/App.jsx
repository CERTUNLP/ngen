import React, { useState } from "react";
import { BrowserRouter } from "react-router-dom";
import { useIdleTimer } from "react-idle-timer";

import routes, { renderRoutes } from "./routes";
import { logout, refreshToken } from "./api/services/auth";
import Alert from "./components/Alert/Alert";
import { getCurrentAccount } from "utils/permissions";

const App = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const onIdle = () => {
    if (getCurrentAccount()?.token) {
      logout(true);
    }
  };

  const onAction = () => {
    const account = getCurrentAccount();
    const token = account?.token;
    const iat = account?.iat;
    const exp = account?.exp;
    if (!token || !iat || !exp) {
      return;
    }
    const currentTime = Date.now() / 1000;
    const secondsWindow = 60; // TODO: Change to backend configuration

    if (iat + secondsWindow < currentTime) {
      if (!isRefreshing) {
        setIsRefreshing(true);
        refreshToken()
          .catch(() => {
            logout(true);
          })
          .finally(() => {
            setIsRefreshing(false);
          });
      }
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
    eventsThrottle: 1000,
    crossTab: true,
    name: "idle-timer",
    syncTimers: 1000
  });

  return (
    <>
      <Alert component="all" />
      <BrowserRouter basename={import.meta.env.VITE_APP_BASE_NAME}>{renderRoutes(routes)}</BrowserRouter>
    </>
  );
};

export default App;
