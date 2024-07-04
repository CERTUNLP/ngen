import { combineReducers } from '@reduxjs/toolkit';
import { reducer as formReducer } from 'redux-form';
import accountReducer from './accountReducer';
import messageReducer from './messageReducer';

import { persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

const reducers = combineReducers({
    account: persistReducer(
        {
            key: 'account',
            storage,
            keyPrefix: 'ngen-'
        },
        accountReducer
    ),
    message: persistReducer(
        {
            key: 'message',
            storage,
            keyPrefix: 'ngen-'
        },
        messageReducer
    ),
    form: formReducer
});

export default reducers;
