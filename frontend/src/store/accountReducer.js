// action - state management
import { LOGIN, LOGOUT, REFRESH_TOKEN, REGISTER } from './actions';

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
      const { user, token } = action.payload;
      return {
        ...state,
        isLoggedIn: true,
        user: user,
        token: token
      };
    }
    case LOGOUT: {
      return {
        ...state,
        isLoggedIn: false,
        token: '',
        user: null
      };
    }
    case REFRESH_TOKEN: {
      const { token } = action.payload;
      return {
        ...state,
        token: token
      };
    }
    default: {
      return { ...state };
    }
  }
};

export default auth;
