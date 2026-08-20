import { COMPONENT_URL } from "../../config/constant";

const STATUS_KEY = "ngen_health_status";
const LEADER_KEY = "ngen_health_leader";
const POLL_INTERVAL = 3000;
const LEADER_TTL = 2 * POLL_INTERVAL + 1000;

let channel = null;
try {
  channel = new BroadcastChannel("ngen_health");
} catch (e) {
  channel = null;
}

let leaderTimer = null;
let watchdogTimer = null;
let releaseLock = null;
let started = false;
const subscribers = new Set();

const getApiServer = () => localStorage.getItem("API_SERVER");

const notify = (status) => {
  subscribers.forEach((cb) => cb(status));
};

const setStatus = (status) => {
  localStorage.setItem(STATUS_KEY, status);
  notify(status);
  try {
    channel && channel.postMessage({ type: "status", status });
  } catch (e) {
    // ignore
  }
};

const checkNow = async () => {
  const apiServer = getApiServer();
  if (!apiServer) {
    setStatus("down");
    return;
  }
  try {
    const res = await fetch(apiServer + COMPONENT_URL.health, { cache: "no-store" });
    setStatus(res.ok ? "up" : "down");
  } catch (e) {
    setStatus("down");
  }
};

const stopLeading = () => {
  if (leaderTimer) {
    clearInterval(leaderTimer);
    leaderTimer = null;
  }
};

const tick = () => {
  localStorage.setItem(LEADER_KEY, String(Date.now()));
  if (!document.hidden) {
    checkNow();
  }
};

const startLeadingFallback = () => {
  stopLeading();
  tick();
  leaderTimer = setInterval(tick, POLL_INTERVAL);
};

const acquireLeadership = () => {
  if (navigator.locks && navigator.locks.request) {
    navigator.locks
      .request("ngen_health_leader", async () => {
        if (!started) return;
        tick();
        leaderTimer = setInterval(tick, POLL_INTERVAL);
        return new Promise((resolve) => {
          releaseLock = resolve;
        });
      })
      .catch(() => {
        // ignore
      });
  } else {
    startLeadingFallback();
    if (!watchdogTimer) {
      watchdogTimer = setInterval(() => {
        const last = Number(localStorage.getItem(LEADER_KEY) || "0");
        if (!Number.isFinite(last) || Date.now() - last > LEADER_TTL) {
          startLeadingFallback();
        }
      }, LEADER_TTL);
    }
  }
};

export const releaseLeadership = () => {
  stopLeading();
  if (releaseLock) {
    releaseLock();
    releaseLock = null;
  }
  localStorage.setItem(LEADER_KEY, "0");
};

export const getHealthStatus = () => localStorage.getItem(STATUS_KEY);

export const subscribeHealth = (callback) => {
  subscribers.add(callback);

  if (!started) {
    started = true;

    window.addEventListener("storage", (e) => {
      if (e.key === STATUS_KEY) notify(e.newValue);
    });

    if (channel) {
      channel.onmessage = (e) => {
        if (e.data?.type === "status") notify(e.data.status);
      };
    }

    window.addEventListener("focus", () => {
      acquireLeadership();
      notify(getHealthStatus());
    });
  }

  acquireLeadership();
  callback(getHealthStatus());

  return () => {
    subscribers.delete(callback);
  };
};
