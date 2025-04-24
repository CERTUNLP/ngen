import { useState, useEffect } from "react";
import { useIdleTimer } from "react-idle-timer";
import { getCurrentAccount } from "utils/permissions";
import { refreshToken, logout } from "api/services/auth";
import { getSettingJWTRefreshTokenLifetime } from "api/services/setting";

export const useTokenManager = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [timeout, setTimeoutValue] = useState(null);

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
    const secondsWindow = Math.floor((exp - iat) * 0.75);
  
    if (exp - secondsWindow < currentTime) {
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

  useEffect(() => {
    getSettingJWTRefreshTokenLifetime(false).then((val) => {
      const timeoutInMs = 1000 * parseInt(val);
      setTimeoutValue(timeoutInMs);
    });
  }, []);

  useIdleTimer({
    onIdle,
    onAction,
    timeout: timeout ?? 1000 * 15 * 60, // default 15 minutes
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
};
