// import { useDispatch as useReduxDispatch, useSelector as useReduxSelector } from 'react-redux';
// import { persistStore } from 'redux-persist';
import { configureStore } from '@reduxjs/toolkit';
// import { thunk } from 'redux-thunk';
//
//
import reducers from './reducers';
//
// // const nonSerializableMiddleware = store => next => action => {
// //   if (action.type === 'persist/PERSIST') {
// //     // Handle non-serializable values here
// //     const { register, rehydrate, ...serializableAction } = action;
// //     // Store or use the non-serializable values as needed
// //     // For example, you can call the functions directly here
// //     if (register) register();
// //     if (rehydrate) rehydrate();
// //     return next(serializableAction);
// //   }
// //   return next(action);
// // };
//

const store = configureStore({
  reducer: reducers,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false
    }),
  devTools: true
});
//
// // export const useSelector = useReduxSelector;
//
// // export const useDispatch = () => useReduxDispatch();
//
// const persister = persistStore(store);
//
// export { store, persister };
export default store;
