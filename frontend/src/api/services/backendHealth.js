const CHANNEL_NAME = "ngen_health";
const LOCK_NAME = "ngen_health_leader";
const STATUS_KEY = "ngen_health_status";

let channel = null;
try {
  channel = new BroadcastChannel(CHANNEL_NAME);
} catch (e) {
  channel = null;
}

export const readCachedStatus = () => localStorage.getItem(STATUS_KEY);

export const writeCachedStatus = (status) => {
  localStorage.setItem(STATUS_KEY, status);
};

export const publishHealthStatus = (status) => {
  try {
    channel && channel.postMessage({ status });
  } catch (e) {
    // ignore
  }
};

export const subscribeHealthStatus = (callback) => {
  if (channel) {
    channel.onmessage = (e) => {
      if (e.data?.status) callback(e.data.status);
    };
  }
  return () => {};
};

export const subscribeLeadership = (callback) => {
  if (!navigator.locks || !navigator.locks.request) {
    callback(true);
    return () => {};
  }

  let cancelled = false;
  let release = null;

  navigator.locks.request(LOCK_NAME, async () => {
    if (cancelled) return;
    callback(true);
    return new Promise((resolve) => {
      release = resolve;
    });
  });

  return () => {
    cancelled = true;
    release && release();
  };
};
