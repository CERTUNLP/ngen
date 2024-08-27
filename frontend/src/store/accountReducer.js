// action - state management
import { LOGIN, LOGOUT, REFRESH_TOKEN, REGISTER, SAVE_URL } from './actions';

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
      const { user, token, iat, exp, user_id } = action.payload;
      return {
        ...state,
        isLoggedIn: true,
        user: user,
        token: token,
        iat: iat,
        exp: exp,
        user_id: user_id
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
        user: null
      };
    }
    case REFRESH_TOKEN: {
      const { token, iat, exp } = action.payload;
      return {
        ...state,
        token: token,
        isLoggedIn: true,
        isInitialized: true,
        iat: iat,
        exp: exp
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
