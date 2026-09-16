import { beforeEach, describe, expect, it, vi } from "vitest";

/**
 * What is covered here is the part of a session that depends on when things
 * happen: two places asking for a new token at the same moment, an answer that
 * arrives after the user logged out, and being refused for asking too often.
 * All of it was found by hand with a browser, and none of it is something a
 * build catches.
 */

const post = vi.fn();
const dispatch = vi.fn();
const setAlert = vi.fn();
let state;

vi.mock("../api", () => ({
  default: {
    post: (...args) => post(...args)
  }
}));
vi.mock("../../store", () => ({
  default: {
    dispatch: (...args) => dispatch(...args),
    getState: () => state
  }
}));
vi.mock("../../utils/setAlert", () => ({
  default: (...args) => setAlert(...args)
}));
vi.mock("i18next", () => ({
  default: { t: (key) => key }
}));

const REFRESH_URL = "ctoken/refresh/";
const LOGOUT_URL = "ctoken/logout/";

// The server writes these with its own clock, an hour away from the one here
const SERVER_IAT = 1000000;
const SERVER_EXP = SERVER_IAT + 300;

const accessToken = (iat = SERVER_IAT, exp = SERVER_EXP) =>
  `header.${btoa(JSON.stringify({ token_type: "access", iat, exp, user_id: "1" }))}.signature`;

const answers = (access = accessToken()) => ({ data: { access } });

const throttled = (retryAfter) => ({
  response: {
    status: 429,
    headers: { "retry-after": String(retryAfter) },
    data: { detail: "Request was throttled." }
  }
});

const neverAnswers = () => new Promise(() => {});

let auth;

beforeEach(async () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-01-01T00:00:00Z"));
  post.mockReset();
  dispatch.mockReset();
  setAlert.mockReset();
  state = { account: { token: "the one of the session" } };
  // The store answers what was dispatched to it, which is what says whether
  // there is a session left at all
  dispatch.mockImplementation((action) => {
    if (action?.type === "LOGOUT") {
      state = { account: { token: "" } };
    }
    if (action?.type === "LOGIN" || action?.type === "REFRESH_TOKEN") {
      state = { account: { token: action.payload.token } };
    }
  });
  localStorage.clear();
  // The session lives in the state of the module, so every case gets its own
  vi.resetModules();
  auth = await import("./auth");
});

describe("what is kept together with a token", () => {
  it("takes its life from the server and its age from the clock that asks", () => {
    const payload = auth.sessionPayload(accessToken());

    expect(payload.lifetime).toBe(300);
    expect(payload.obtainedAt).toBe(Date.now());
    // The two clocks disagree and it changes nothing, because nothing here is
    // a comparison between them
    expect(payload.obtainedAt).not.toBe(SERVER_IAT * 1000);
  });
});

describe("asking for a new token", () => {
  it("gives the two callers the one answer that is already travelling", async () => {
    let answer;
    post.mockImplementation(() => new Promise((resolve) => (answer = resolve)));

    const onActivity = auth.refreshToken();
    const afterA401 = auth.refreshToken();

    expect(afterA401).toBe(onActivity);
    expect(post).toHaveBeenCalledTimes(1);

    answer(answers());
    await expect(onActivity).resolves.toBeTruthy();
  });

  it("stores what came back", async () => {
    post.mockResolvedValue(answers());

    await auth.refreshToken();

    const [action] = dispatch.mock.calls.at(-1);
    expect(action.type).toBe("REFRESH_TOKEN");
    expect(action.payload.lifetime).toBe(300);
    expect(action.payload.obtainedAt).toBe(Date.now());
  });

  it("refuses another one before the wait is over, without asking the api", async () => {
    post.mockResolvedValue(answers());
    await auth.refreshToken();

    vi.advanceTimersByTime(14000);
    await expect(auth.refreshToken()).rejects.toMatchObject({ renewalPostponed: true });
    expect(post).toHaveBeenCalledTimes(1);

    vi.advanceTimersByTime(1000);
    await auth.refreshToken();
    expect(post).toHaveBeenCalledTimes(2);
  });

  it("waits what the api asks for, and never less than the floor", async () => {
    // The api answers with what is left of its window over the requests that
    // fit in it, so one second is a number it gives often
    post.mockRejectedValueOnce(throttled(1));
    await expect(auth.refreshToken()).rejects.toBeTruthy();

    vi.advanceTimersByTime(1500);
    await expect(auth.refreshToken()).rejects.toMatchObject({ renewalPostponed: true });
    expect(post).toHaveBeenCalledTimes(1);

    post.mockResolvedValue(answers());
    vi.advanceTimersByTime(14000);
    await auth.refreshToken();
    expect(post).toHaveBeenCalledTimes(2);
  });

  it("waits longer when the api asks for longer", async () => {
    post.mockRejectedValueOnce(throttled(60));
    await expect(auth.refreshToken()).rejects.toBeTruthy();

    vi.advanceTimersByTime(30000);
    await expect(auth.refreshToken()).rejects.toMatchObject({ renewalPostponed: true });

    post.mockResolvedValue(answers());
    vi.advanceTimersByTime(31000);
    await auth.refreshToken();
    expect(post).toHaveBeenCalledTimes(2);
  });
});

describe("a session that is being closed", () => {
  it("does not keep a token that comes back after the logout was asked for", async () => {
    let answer;
    post.mockImplementation((url) => (url === REFRESH_URL ? new Promise((resolve) => (answer = resolve)) : Promise.resolve({})));

    const renewal = auth.refreshToken();
    auth.logout();
    answer(answers());

    await expect(renewal).rejects.toMatchObject({ sessionClosed: true });
    expect(dispatch.mock.calls.map(([action]) => action.type)).not.toContain("REFRESH_TOKEN");
  });

  it("asks for no new token while the logout is travelling", async () => {
    post.mockImplementation((url) => (url === LOGOUT_URL ? neverAnswers() : Promise.resolve(answers())));

    auth.logout();
    await vi.advanceTimersByTimeAsync(0);
    const asked = post.mock.calls.length;

    await expect(auth.refreshToken()).rejects.toMatchObject({ sessionClosed: true });
    // Longer than the wait between renewals, which is what used to let the
    // activity of the user start one every fifteen seconds
    vi.advanceTimersByTime(60000);
    await expect(auth.refreshToken()).rejects.toMatchObject({ sessionClosed: true });

    expect(post).toHaveBeenCalledTimes(asked);
  });

  it("drops a renewal that is travelling instead of racing it", async () => {
    // Rotation hands back a new cookie and the browser writes it whether
    // anything is listening or not, so an answer that lands after the session
    // was revoked would put a valid token back. Waiting for it means picking a
    // number, and an answer slower than that number does it anyway
    let signal;
    post.mockImplementation((url, _body, config) => {
      if (url === REFRESH_URL) {
        signal = config.signal;
        return neverAnswers();
      }
      return Promise.resolve({});
    });

    auth.refreshToken();
    await auth.logout();

    expect(signal.aborted).toBe(true);
    expect(post.mock.calls.filter(([url]) => url === LOGOUT_URL)).toHaveLength(1);
  });

  it("says out loud that the application is the one closing the session", async () => {
    post.mockResolvedValue({});

    await auth.logout();

    const [, , config] = post.mock.calls.find(([url]) => url === LOGOUT_URL);
    expect(config.headers["X-Requested-With"]).toBe("XMLHttpRequest");
  });

  it("closes the session in the browser without waiting for the api to answer", async () => {
    // The instance has no timeout, so a connection that stalls used to leave
    // the browser sitting on a session it was told to close
    post.mockImplementation((url) => (url === LOGOUT_URL ? neverAnswers() : Promise.resolve(answers())));

    auth.logout();

    expect(dispatch.mock.calls.map(([action]) => action.type)).toContain("LOGOUT");
    await expect(auth.refreshToken()).rejects.toMatchObject({ sessionClosed: true });
  });

  it("renews nothing once there is no session left in the store", async () => {
    // The refresh cookie outlives the logout, so an answer to a request that
    // was already travelling could hand a token back to a browser that nobody
    // is logged into
    post.mockResolvedValue(answers());
    state = { account: { token: "" } };

    await expect(auth.refreshToken()).rejects.toMatchObject({ sessionClosed: true });
    expect(post).not.toHaveBeenCalled();
  });

  it("says it once and closes it once, however many callers find out", async () => {
    post.mockImplementation((url) => (url === LOGOUT_URL ? neverAnswers() : Promise.resolve(answers())));

    auth.endSession();
    auth.endSession();
    auth.endSession();
    await vi.advanceTimersByTimeAsync(0);

    expect(setAlert).toHaveBeenCalledTimes(1);
    expect(post.mock.calls.filter(([url]) => url === LOGOUT_URL)).toHaveLength(1);
  });
});

describe("telling a session that is over from a moment that passes", () => {
  it.each([
    ["the api says the refresh token is not valid", { response: { data: { code: "token_not_valid" } } }, true],
    ["being refused for asking too often", throttled(30), false],
    ["a backend that is restarting", { response: { status: 502, data: "<html>502 Bad Gateway</html>" } }, false],
    ["the network dropped", { message: "Network Error" }, false]
  ])("%s", (_case, error, isOver) => {
    expect(auth.isSessionExpired(error)).toBe(isOver);
  });
});
