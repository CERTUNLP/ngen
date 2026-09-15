import { useState, useEffect, useRef } from "react";
import { useIdleTimer } from "react-idle-timer";
import { getCurrentAccount } from "utils/permissions";
import { refreshToken, logout, isSessionExpired } from "api/services/auth";
import { getSettingJWTRefreshTokenLifetime } from "api/services/setting";
import setAlert from "utils/setAlert";
import i18next from "i18next";

// A token is renewed once this much of its life is gone, so the rest is left as
// margin for a slow answer or for a couple of tries that did not work. How
// often a renewal may be asked for at all, and how long to wait after one that
// failed, is decided by the service: the retry of a request that got a 401 asks
// for the same thing and the two have to wait together
const RENEW_AFTER = 0.75;
const DEFAULT_IDLE_MS = 15 * 60 * 1000;

export const useTokenManager = () => {
  const [timeout, setTimeoutValue] = useState(null);
  // Refs and not state: this is read inside a callback that the idle timer
  // calls once a second, and a value that only arrives with the next render
  // leaves a window where two renewals start at the same time
  const refreshing = useRef(false);
  const refreshLifetime = useRef(null);

  // Landing on the login screen with nothing said is what the report of this
  // looked like from the outside: a session that ends has to say so
  const endSession = () => {
    setAlert(i18next.t("ngen.auth.session_expired"), "error");
    logout(true);
  };

  const onIdle = () => {
    if (getCurrentAccount()?.token) {
      logout(true);
    }
  };

  const onAction = () => {
    const account = getCurrentAccount();
    if (!account?.token) {
      return;
    }

    // Only durations travel between the clock of the server and the clock of
    // the browser: how long a token lasts is read from what the server signed,
    // how old it is from the moment it arrived here, measured with the clock
    // that is asking. Comparing exp against Date.now() asked for a new token on
    // every mouse move of every browser whose clock did not agree with the one
    // of the server, until the api refused and the session was thrown away
    const lifetime = (account.lifetime ?? account.exp - account.iat) * 1000;
    if (!lifetime || lifetime < 0) {
      return;
    }
    // A session stored before any of this existed has no obtainedAt, and
    // renewing it once is what gives it one
    const age = account.obtainedAt ? Date.now() - account.obtainedAt : lifetime;

    // Past this there is no refresh token left to renew anything with, so there
    // is nothing to wait for anymore
    if (refreshLifetime.current && age > refreshLifetime.current) {
      endSession();
      return;
    }

    if (age < lifetime * RENEW_AFTER || refreshing.current) {
      return;
    }

    refreshing.current = true;
    refreshToken()
      .catch((error) => {
        // Only the api saying that the refresh token is not valid anymore ends
        // the session. Being refused for asking too often, a backend that is
        // restarting or a network that dropped are moments that pass, and
        // throwing the user out on those loses the work on the screen. The
        // service is the one that knows how long to wait before trying again
        if (isSessionExpired(error)) {
          endSession();
        }
      })
      .finally(() => {
        refreshing.current = false;
      });
  };

  useEffect(() => {
    getSettingJWTRefreshTokenLifetime(false).then((val) => {
      const seconds = parseInt(val);
      if (Number.isFinite(seconds) && seconds > 0) {
        refreshLifetime.current = 1000 * seconds;
        setTimeoutValue(1000 * seconds);
      }
    });
  }, []);

  useIdleTimer({
    onIdle,
    onAction,
    timeout: timeout ?? DEFAULT_IDLE_MS,
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
