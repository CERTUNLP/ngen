// action - state management
import { LOGIN, LOGOUT, REFRESH_TOKEN, REGISTER, SAVE_URL } from "./actions";

// initial state
export const initialState = {
  isLoggedIn: false,
  isInitialized: false,
  user: null
};

// ==============================|| AUTH REDUCER ||============================== //

const auth = (state = initialState, action) => {
  switch (action.type) {
    case REGISTER: {
      const { user } = action.payload;
      return {
        ...state,
        user
      };
    }
    case LOGIN: {
      const { user, token, iat, exp, user_id, lifetime, obtainedAt } = action.payload;
      return {
        ...state,
        isLoggedIn: true,
        user: user,
        token: token,
        iat: iat,
        exp: exp,
        user_id: user_id,
        // How long the token lasts and when it got here, the two the renewal
        // reads: measured against each other they do not need the clock of the
        // browser to agree with the clock of the server
        lifetime: lifetime,
        obtainedAt: obtainedAt
      };
    }
    case LOGOUT: {
      return {
        ...state,
        isLoggedIn: false,
        token: "",
        iat: null,
        exp: null,
        user_id: null,
        user: null,
        lifetime: null,
        obtainedAt: null
      };
    }
    case REFRESH_TOKEN: {
      const { token, iat, exp, lifetime, obtainedAt } = action.payload;
      return {
        ...state,
        token: token,
        isLoggedIn: true,
        isInitialized: true,
        iat: iat,
        exp: exp,
        lifetime: lifetime,
        obtainedAt: obtainedAt
      };
    }
    case SAVE_URL: {
      const { url } = action.payload;
      return {
        ...state,
        last_url: url
      };
    }
    default: {
      return { ...state };
    }
  }
};

export default auth;
